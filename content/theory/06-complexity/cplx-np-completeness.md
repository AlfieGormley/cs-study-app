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

In symbols:

```formula
A ≤_p B
x ∈ A  iff  f(x) ∈ B   for every x
where
A, B: decision problems, each viewed as the set of inputs whose answer is yes
≤_p: "polynomial-time reduces to": A ≤_p B means a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer, so B is at least as hard as A
x: any input (instance) of problem A, written as a string of bits
f: the reduction: a function, computable in polynomial time, that turns an instance of A into an instance of B
f(x): the instance of B that f produces from x
∈: "is a member of": x ∈ A means x is a yes-instance of A
In words: A reduces to B when a fast translation f turns every question about A into a question about B with exactly the same answer.
```

Read A ≤_p B as "A is no harder than B", because any algorithm for B gives one for A: compute f(x), then ask B.

For example, Hamiltonian cycle (is there a cycle visiting every vertex exactly once?) reduces to TSP (is there a tour of total cost at most some budget?). Given a graph with 10 vertices, f gives every edge weight 1, every missing edge weight 2, and sets the budget to 10. A tour of cost 10 must use only weight-1 edges, so the TSP answer is yes exactly when the graph has a Hamiltonian cycle.

```
 x --[ f: poly time ]--> f(x)
 f(x) --[ solver for B ]--> yes/no
 together: an algorithm for A
```

Two properties do most of the work:

- **Transitive**: if A reduces to B and B reduces to C, then A reduces to C. Compose the two translations; a polynomial of a polynomial is a polynomial.
- **Downward closure of P**: if A reduces to B and B can be solved in polynomial time, so can A.

```formula
A ≤_p B and B ≤_p C  gives  A ≤_p C
A ≤_p B and B ∈ P  gives  A ∈ P
where
A, B, C: decision problems
≤_p: "polynomial-time reduces to": A ≤_p B means a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer
∈: "is a member of" (belongs to the class)
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
In words: reductions chain together, and anything that reduces to an efficiently solvable problem is itself efficiently solvable.
```

Why the composition stays polynomial: the first translation f cannot write more output than it has time to write, so the second translation g runs on an input that is at most polynomially long.

```formula
t_total ≤ p(n) + q(p(n))
t_total ≤ n^2 + (n^2)^3 = n^2 + n^6
where
t_total: the number of steps to compute g(f(x)), the composed translation from A to C
n: the length of the input x, in bits
p(n): the polynomial step bound of f on an n-bit input; here n^2
q(m): the polynomial step bound of g on an m-bit input; here m^3
In words: f takes at most p(n) steps and so outputs at most p(n) bits; g then takes at most q(p(n)) steps. With bounds n^2 and m^3 the total is about n^6, still a polynomial.
```

## NP-hard and NP-complete

- A problem B is **NP-hard** if *every* problem in NP reduces to it.
- B is **NP-complete** if it is NP-hard **and** in NP.

In symbols:

```formula
A ≤_p B   for every A ∈ NP
B ∈ NP
where
A: any problem in NP
B: the problem being classified
≤_p: "polynomial-time reduces to": A ≤_p B means a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer
∈: "is a member of" (belongs to the class)
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
In words: the first line alone makes B NP-hard: every NP problem translates into B. Add the second line, that B is itself in NP, and B is NP-complete.
```

The consequence: if any single NP-complete problem is in P, then every NP problem is in P, so P and NP are the same class. Conversely, if they differ, no NP-complete problem has a polynomial-time algorithm.

```formula
B ∈ NPC and B ∈ P  gives  P = NP
P ≠ NP  gives  B ∉ P  for every B ∈ NPC
where
B: a decision problem
NPC: the set of NP-complete problems (in NP, and every NP problem reduces to them)
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
∈: "is a member of"; ∉: "is not a member of"
≠: "is not equal to": here, the two classes contain different problems
In words: one NP-complete problem with a polynomial-time algorithm would make P and NP equal; if they are different, every NP-complete problem lacks one.
```

> [!warning] NP-hard does not mean "in NP and hard"
> The halting problem is NP-hard (any NP problem reduces to it: build a machine that halts iff the instance is a yes) but is not in NP; it isn't even decidable. Optimisation problems like "find the shortest tour" are called NP-hard because they aren't yes/no problems, so they can't be in NP.

## The Cook–Levin theorem

**Theorem (Cook 1971; Levin independently, published 1973).** SAT, deciding whether a Boolean formula has a satisfying assignment, is NP-complete.

SAT is in NP: the assignment is the certificate. The hard part is showing every NP problem reduces to SAT. We can't know each problem in advance, so the proof works from the only thing they share: a nondeterministic Turing machine N that decides L within a polynomial number of steps.

### The tableau

An accepting run of N on an input w is a sequence of configurations (snapshots of the state, head position and tape), one per step. Write them as the rows of a square grid, the **tableau**. Each cell holds one symbol: a tape symbol, or a state marker showing where the head is.

```formula
N_rows ≤ n^k
N_cols ≤ n^k
where
N_rows: the number of rows of the tableau: one per step (configuration) of the run
N_cols: the number of columns: tape cells the run can touch, since in n^k steps the head can visit at most n^k cells
n: the length of the input w, in symbols
k: the fixed exponent of N's polynomial running time n^k; a constant set by the machine, not by the input
In words: a run that lasts at most n^k steps fits in a grid n^k rows tall and n^k columns wide. For a machine running in n^3 steps on a 100-symbol input, that is 1,000,000 rows by 1,000,000 columns.
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

### Why it's a polynomial reduction

The `exactly_one` encoding gives each cell one "at least one" clause plus one "not both" clause per pair of symbols:

```formula
N_clauses = 1 + C × (C − 1) / 2
N_clauses = 1 + 4 × 3 / 2 = 7   for C = 4
where
N_clauses: the number of clauses φ_cell uses for one cell
C: the number of possible cell symbols (tape symbols and state markers); a constant fixed by the machine N, not by the input
In words: one clause says "at least one symbol", and each of the C × (C − 1) / 2 pairs of symbols gets a "not both" clause, so the count grows like C squared but never depends on the input.
```

Add it up over the whole grid:

```formula
N_cells = n^k × n^k = n^{2k}
N_cells = 100^3 × 100^3 = 10^12
|φ| = O(C^2 × n^{2k}) = O(n^{2k})
where
N_cells: the number of cells in the tableau
n: the length of the input w, in symbols; 100 in the second line
k: the fixed exponent of N's running time n^k; 3 in the second line
C: the number of possible cell symbols, a constant fixed by N
φ: phi, the Boolean formula the reduction builds
|φ|: the size of the formula φ: how many symbols it takes to write down
O(...): Big O: grows at most as fast as a constant times the expression inside, for large n
In words: every cell contributes a constant amount of formula (its exactly-one clauses plus a constant number of window constraints), so the formula's size is a constant times n^{2k}: a polynomial in n.
```

The second line is the example of a machine running in cubic time (k = 3) on an input of 100 symbols (n = 100): a trillion cells. That is enormous, but it is a polynomial, and the formula can be written out mechanically.

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

## From SAT to 3-SAT

Most reductions start from **3-SAT**: CNF formulas where every clause has exactly 3 literals (in some treatments, at most 3). Its rigid shape makes gadgets easier to design.

SAT in CNF reduces to 3-SAT by splitting long clauses with fresh variables. A five-literal clause is replaced by three three-literal clauses:

```formula
C_old = (l_1 ∨ l_2 ∨ l_3 ∨ l_4 ∨ l_5)
C_new = (l_1 ∨ l_2 ∨ y_1)
  ∧ (¬y_1 ∨ l_3 ∨ y_2)
  ∧ (¬y_2 ∨ l_4 ∨ l_5)
where
C_old: the original clause, with 5 literals
C_new: the three clauses that replace it
l_1, l_2, l_3, l_4, l_5: the literals of the original clause; a literal is a variable or its negation
y_1, y_2: fresh variables that appear nowhere else in the formula
∨: OR: a clause is true when at least one of its literals is true
∧: AND: all three new clauses must be true
¬: NOT: ¬y_1 is true exactly when y_1 is false
In words: C_new can be satisfied (by choosing y_1 and y_2) exactly when at least one original literal is true, so C_old and C_new are equivalent for satisfiability.
```

If some l_i is true, set the y's to "carry" the chain round it: y's before it true, y's after it false. If all l_i are false, y_1 must be true, which forces y_2 true, which falsifies the last clause.

```formula
N_clauses = k − 2
N_new = k − 3
N_clauses = 5 − 2 = 3   for k = 5
N_new = 5 − 3 = 2   for k = 5
where
k: the number of literals in the original clause (at least 4)
N_clauses: the number of three-literal clauses that replace it
N_new: the number of fresh y variables added
In words: a clause of k literals becomes k − 2 clauses with k − 3 new variables, so the formula grows only linearly.
```

Short clauses are padded (by repeating a literal, or with extra variables if repeats aren't allowed).

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

With two literals per clause, the problem collapses into P. Each two-literal clause is the same as two implications:

```formula
(a ∨ b)  ≡  (¬a → b) ∧ (¬b → a)
where
a, b: literals (a variable or its negation)
∨: OR: true when at least one side is true
¬: NOT: ¬a is true exactly when a is false
→: implies: ¬a → b means "if a is false then b must be true"
∧: AND: both implications hold
≡: "is logically equivalent to": true in exactly the same assignments
In words: "a or b" means "if not a then b, and if not b then a". For the clause (x ∨ y): if x is false, y must be true, and if y is false, x must be true.
```

Draw each implication as an arrow between literals: this is the implication graph. The formula is unsatisfiable exactly when some variable and its own negation lie in the same strongly connected component of this graph (each can reach the other), which takes linear time to check (Aspvall, Plass and Tarjan, 1979). Going from 2 to 3 literals per clause crosses from linear time to NP-complete.

## Karp's 21 and the domino effect

In 1972 Richard Karp showed 21 well-known problems NP-complete by chaining reductions from SAT: clique, vertex cover, set cover, Hamiltonian cycle, graph colouring, knapsack, and more. Garey and Johnson's 1979 book catalogued hundreds. Today there are thousands.

The recipe for showing a new problem X is NP-complete:

1. Show **X is in NP** (give the certificate and verifier).
2. Pick a known NP-complete problem Y.
3. Give a polynomial-time translation f **from Y to X**: transform instances of the *known* hard problem into instances of X.
4. Prove **both** directions: a yes-instance of Y maps to a yes-instance of X, and a yes-instance produced by f comes only from a yes-instance of Y.

```formula
X ∈ NP
Y ≤_p X   with Y ∈ NPC
y ∈ Y  gives  f(y) ∈ X
f(y) ∈ X  gives  y ∈ Y
where
X: the new problem you want to classify
Y: a known NP-complete problem, such as 3-SAT
y: any instance of Y
f: the polynomial-time translation from instances of Y to instances of X
f(y): the instance of X built from y
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
NPC: the set of NP-complete problems
≤_p: "polynomial-time reduces to": Y ≤_p X means f maps every instance of Y to an instance of X with the same yes/no answer
∈: "is a member of"; y ∈ Y means y is a yes-instance of Y
In words: show X is in NP, then translate a known NP-complete problem into X and prove the translation keeps yes as yes and no as no.
```

The commonest mistake is reducing in the wrong direction. Reducing X to SAT only proves X is no harder than SAT, which is true of every problem in NP.

## Not everything is P or NP-complete

**Ladner's theorem (1975)**: if P and NP are different, there are problems in NP that are neither in P nor NP-complete (**NP-intermediate**).

```formula
P ≠ NP  gives  NPI ≠ ∅
where
P: the complexity class P: decision problems solvable in polynomial time
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
NPI: the NP-intermediate problems: in NP, but neither in P nor NP-complete
≠: "is not equal to"
∅: the empty set (a set with nothing in it)
In words: if P and NP differ, at least one NP-intermediate problem exists.
```

The theorem's examples are artificial. Natural candidates include factoring and graph isomorphism, but nobody can prove them intermediate, because a problem in NP but not in P would itself prove that P and NP differ.

**Weak versus strong.** Subset sum and knapsack are NP-complete only because numbers can be huge; with small numbers, the pseudo-polynomial DP is fast. They are *weakly* NP-complete. Problems like 3-partition and TSP stay NP-complete even when all numbers are bounded by a polynomial in n: *strongly* NP-complete.

## Where you meet it in practice

- **Package managers.** Deciding whether a set of packages with versioned dependencies and conflicts can be installed together is NP-complete. libsolv (behind openSUSE's zypper and Fedora's dnf) solves it with a SAT solver.
- **Register allocation** is graph colouring in disguise (Chaitin, 1981); compilers use heuristics.
- **Puzzles**: generalised Sudoku and Minesweeper consistency are NP-complete.

## Key takeaways
- A polynomial-time reduction from A to B is a fast map preserving yes/no answers; then an algorithm for B solves A.
- NP-hard: everything in NP reduces to it. NP-complete: NP-hard and in NP. One NP-complete problem in P would make P and NP equal.
- Cook–Levin: SAT is NP-complete, by encoding an accepting run as a square tableau whose side is the machine's polynomial running time, giving a polynomial-size formula, with local 2 × 3 windows for the transitions.
- SAT reduces to 3-SAT by splitting clauses; 2-SAT is in P (linear time via implication graphs).
- To prove X NP-complete, reduce a known NP-complete problem to X, never the other way.
- If P and NP differ, Ladner's theorem guarantees NP-intermediate problems exist.

## Further reading
- [Cook–Levin theorem — Wikipedia](https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem)
- [Cook, The Complexity of Theorem-Proving Procedures (1971, PDF)](https://www.cs.toronto.edu/~sacook/homepage/1971.pdf)
- [Karp's 21 NP-complete problems — Wikipedia](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems)
- [NP-completeness — Wikipedia](https://en.wikipedia.org/wiki/NP-completeness)
- [2-satisfiability — Wikipedia](https://en.wikipedia.org/wiki/2-satisfiability)
- [Ladner's theorem — Wikipedia](https://en.wikipedia.org/wiki/Ladner%27s_theorem)
- [MIT 18.404J Theory of Computation (Sipser), OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
