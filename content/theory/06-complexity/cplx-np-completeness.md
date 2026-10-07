---
id: cplx-np-completeness
title: NP-completeness and Cook–Levin
level: intermediate
minutes: 14
summary: Polynomial-time reductions, what NP-hard and NP-complete mean, how the Cook–Levin theorem encodes any NP computation as a SAT formula, and the SAT to 3-SAT step that opens the door to Karp's 21 problems.
---

Thousands of problems in NP have resisted polynomial-time algorithms: scheduling, routing, packing, colouring, satisfiability. In 1971 Stephen Cook found that many of them are secretly the same problem. Solve one efficiently and you have solved them all.

The tool that ties them together is the **reduction**, and the problems at the top of the pile are called **NP-complete**.

## Reductions: "B is at least as hard as A"

A **polynomial-time (many-one, or Karp) reduction** from problem A to problem B is a function f such that:

- f is computable in polynomial time, and
- for every input x: x is a yes-instance of A **if and only if** f(x) is a yes-instance of B.

We write **A ≤p B**. Read it as "A is no harder than B", because any algorithm for B gives one for A: compute f(x), then ask B.

```
 x --[ f: poly time ]--> f(x)
 f(x) --[ solver for B ]--> yes/no
 together: an algorithm for A
```

Two properties do most of the work:

- **Transitive**: if A ≤p B and B ≤p C then A ≤p C (compose the two functions; a polynomial of a polynomial is a polynomial).
- **Downward closure of P**: if A ≤p B and B ∈ P then A ∈ P.

## NP-hard and NP-complete

- A problem B is **NP-hard** if *every* problem in NP reduces to it.
- B is **NP-complete** if it is NP-hard **and** in NP.

The consequence: if any single NP-complete problem is in P, then every NP problem is in P, so P = NP. Conversely, if P ≠ NP, no NP-complete problem has a polynomial-time algorithm.

> [!warning] NP-hard does not mean "in NP and hard"
> The halting problem is NP-hard (any NP problem reduces to it: build a machine that halts iff the instance is a yes) but is not in NP; it isn't even decidable. Optimisation problems like "find the shortest tour" are called NP-hard because they aren't yes/no problems, so they can't be in NP.

## The Cook–Levin theorem

**Theorem (Cook 1971; Levin independently, published 1973).** SAT, deciding whether a Boolean formula has a satisfying assignment, is NP-complete.

SAT is in NP: the assignment is the certificate. The hard part is showing every NP problem reduces to SAT. We can't know each problem in advance, so the proof works from the only thing they share: a nondeterministic Turing machine N that decides L in time n^k.

### The tableau

An accepting run of N on input w (of length n) is a sequence of at most n^k configurations. Write them as the rows of an n^k × n^k grid, the **tableau**. Each cell holds one symbol: a tape symbol, or a state marker showing where the head is.

```
       cell 1  2  3  4  5 ...
row 1   # q0 w1 w2 w3  _ ... #  start
row 2   #  a q3 w2 w3  _ ... #
row 3   #  a  b q7 w3  _ ... #
 ...
row t   #  .  . qacc   ...   #  accept
```

The formula has one variable per (cell, symbol) pair: x[i][j][s] is true when cell (i, j) contains symbol s. Then

φ = φ_cell ∧ φ_start ∧ φ_accept ∧ φ_move

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

### Why it's a polynomial reduction

- The tableau has n^k × n^k = n^2k cells.
- The alphabet of cell symbols is a fixed constant C, set by N, not by the input.
- Each cell contributes O(C²) clauses to φ_cell and a constant number of window constraints to φ_move.

So |φ| is O(n^2k), polynomial in n, and it can be written out mechanically. A satisfying assignment *is* an accepting computation, read off cell by cell; and an accepting computation gives a satisfying assignment. So w ∈ L ⇔ φ is satisfiable.

> [!note] What the nondeterminism becomes
> N's guesses turn into the freedom the SAT solver has in choosing variable values. The formula is fixed; the "guessing" is the existential "is there an assignment?".

## From SAT to 3-SAT

Most reductions start from **3-SAT**: CNF formulas where every clause has exactly 3 literals (in some treatments, at most 3). Its rigid shape makes gadgets easier to design.

SAT in CNF reduces to 3-SAT by splitting long clauses with fresh variables. A clause (l1 ∨ l2 ∨ l3 ∨ l4 ∨ l5) becomes:

```
(l1 ∨ l2 ∨ y1)
(¬y1 ∨ l3 ∨ y2)
(¬y2 ∨ l4 ∨ l5)
```

If some li is true, set the y's to "carry" the chain round it. If all li are false, y1 must be true, which forces y2 true, which falsifies the last clause. A clause of k literals becomes k − 2 clauses with k − 3 new variables: linear blow-up. Short clauses are padded (by repeating a literal, or with extra variables if repeats aren't allowed).

```python
def split(clause, nxt):
    # nxt: next unused variable number
    if len(clause) <= 3:
        return [clause], nxt
    y = nxt; nxt += 1
    out = [[clause[0], clause[1], y]]
    for lit in clause[2:-2]:
        z = nxt; nxt += 1
        out.append([-y, lit, z])
        y = z
    out.append([-y, clause[-2], clause[-1]])
    return out, nxt

print(split([1, 2, 3, 4, 5], 6))
# ([[1, 2, 6], [-6, 3, 7],
#   [-7, 4, 5]], 8)
```

I checked this against brute-force satisfiability on 200 random formulas: the split formula is satisfiable exactly when the original is.

### The edge of tractability: 2-SAT

With two literals per clause, the problem collapses into P. Each clause (a ∨ b) is two implications, ¬a → b and ¬b → a. The formula is unsatisfiable iff some variable x and ¬x lie in the same strongly connected component of this implication graph, which takes linear time to check (Aspvall, Plass and Tarjan, 1979). Going from 2 to 3 literals per clause crosses from linear time to NP-complete.

## Karp's 21 and the domino effect

In 1972 Richard Karp showed 21 well-known problems NP-complete by chaining reductions from SAT: clique, vertex cover, set cover, Hamiltonian cycle, graph colouring, knapsack, and more. Garey and Johnson's 1979 book catalogued hundreds. Today there are thousands.

The recipe for showing a new problem X is NP-complete:

1. Show **X ∈ NP** (give the certificate and verifier).
2. Pick a known NP-complete problem Y.
3. Give a polynomial-time f with **Y ≤p X**: transform instances of the *known* hard problem into instances of X.
4. Prove **both** directions: y yes ⇒ f(y) yes, and f(y) yes ⇒ y yes.

The commonest mistake is reducing in the wrong direction. Showing X ≤p SAT only proves X is no harder than SAT, which is true of every problem in NP.

## Not everything is P or NP-complete

**Ladner's theorem (1975)**: if P ≠ NP, there are problems in NP that are neither in P nor NP-complete (**NP-intermediate**). The theorem's examples are artificial. Natural candidates include factoring and graph isomorphism, but nobody can prove them intermediate, because that would prove P ≠ NP.

**Weak versus strong.** Subset sum and knapsack are NP-complete only because numbers can be huge; with small numbers, the pseudo-polynomial DP is fast. They are *weakly* NP-complete. Problems like 3-partition and TSP stay NP-complete even when all numbers are bounded by a polynomial in n: *strongly* NP-complete.

## Where you meet it in practice

- **Package managers.** Deciding whether a set of packages with versioned dependencies and conflicts can be installed together is NP-complete. libsolv (behind openSUSE's zypper and Fedora's dnf) solves it with a SAT solver.
- **Register allocation** is graph colouring in disguise (Chaitin, 1981); compilers use heuristics.
- **Puzzles**: generalised Sudoku and Minesweeper consistency are NP-complete.

## Key takeaways
- A ≤p B means a polynomial-time map preserving yes/no answers; then an algorithm for B solves A.
- NP-hard: everything in NP reduces to it. NP-complete: NP-hard and in NP. One NP-complete problem in P would give P = NP.
- Cook–Levin: SAT is NP-complete, by encoding an accepting n^k × n^k tableau as a formula of size O(n^2k), using local 2 × 3 windows for the transitions.
- SAT reduces to 3-SAT by splitting clauses; 2-SAT is in P (linear time via implication graphs).
- To prove X NP-complete, reduce a known NP-complete problem to X, never the other way.
- If P ≠ NP, Ladner's theorem guarantees NP-intermediate problems exist.

## Further reading
- [Cook–Levin theorem — Wikipedia](https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem)
- [Cook, The Complexity of Theorem-Proving Procedures (1971, PDF)](https://www.cs.toronto.edu/~sacook/homepage/1971.pdf)
- [Karp's 21 NP-complete problems — Wikipedia](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems)
- [NP-completeness — Wikipedia](https://en.wikipedia.org/wiki/NP-completeness)
- [2-satisfiability — Wikipedia](https://en.wikipedia.org/wiki/2-satisfiability)
- [Ladner's theorem — Wikipedia](https://en.wikipedia.org/wiki/Ladner%27s_theorem)
- [MIT 18.404J Theory of Computation (Sipser), OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
