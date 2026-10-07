---
id: logp-sat
title: Boolean satisfiability intro
level: advanced
minutes: 16
summary: The SAT problem, conjunctive normal form and how to encode real problems into it, why it is NP-complete while 2-SAT and Horn-SAT are easy, and how DPLL and CDCL solvers handle millions of variables in practice.
---

The first lesson ended with a question that sounds trivial: given a propositional formula, is there *any* assignment of true and false to its variables that makes it true? That is the **Boolean satisfiability problem**, or **SAT**.

With n variables there are 2ⁿ assignments to try. SAT was the first problem proved **NP-complete**, which means nobody knows an algorithm that is fast on every input, and finding one would settle P vs NP. Modern SAT solvers can solve large structured industrial formulas, but instance size alone does not predict runtime. They verify chip designs, resolve package dependencies and power program-verification tools.

This lesson is about both halves of that story: why SAT is hard in theory, and why it is so often easy in practice.

## Conjunctive normal form

Solvers take their input in a standard shape, **conjunctive normal form (CNF)**:

- A **literal** is a variable or its negation: x, ¬x.
- A **clause** is an OR of literals: (x ∨ ¬y ∨ z).
- A **CNF formula** is an AND of clauses.

```
(x ∨ y) ∧ (¬x ∨ z) ∧ (¬y ∨ ¬z) ∧ (¬z)
```

To satisfy a CNF formula, every clause must contain at least one true literal. A clause is a constraint: "at least one of these must hold". This is a natural shape for real requirements, which is half the reason CNF is the standard.

Solvers read it in the **DIMACS** format, with variables as numbers and negation as a minus sign. The formula above, with x, y, z as 1, 2, 3:

```
p cnf 3 4
1 2 0
-1 3 0
-2 -3 0
-3 0
```

The header says 3 variables and 4 clauses; each clause ends in 0.

### Converting to CNF

Every formula has an equivalent CNF, found using the laws from the first lesson: eliminate → and ↔, push ¬ inwards with De Morgan, then distribute ∨ over ∧. But distribution can explode:

```
(a1 ∧ b1) ∨ (a2 ∧ b2) ∨ ... ∨ (an ∧ bn)
```

Its equivalent CNF has 2ⁿ clauses, one for each way of picking a or b from every pair.

The fix is the **Tseitin transformation**: introduce a fresh variable for each subformula and add clauses that define it. For a gate x ↔ (a ∧ b):

```
(¬x ∨ a) ∧ (¬x ∨ b) ∧ (x ∨ ¬a ∨ ¬b)
```

The first two say x → a and x → b; the third says (a ∧ b) → x. Add these constraints for every bounded-fan-in gate and a unit clause asserting the root/output variable true. The resulting CNF is linear in formula size. Gate definitions alone do not assert the original formula. It is generally not logically equivalent over the enlarged set of variables, but it is equisatisfiable: satisfiable exactly when the original is. That is all a solver needs.

## Encoding a real problem

The skill that makes SAT useful is **encoding**: turning a problem into clauses. Take graph 3-colouring: can you colour each vertex red, green or blue so no edge joins two vertices of the same colour?

Use a variable v_c meaning "vertex v has colour c". Then:

```
each vertex gets a colour:
  (v_R ∨ v_G ∨ v_B)
at most one colour per vertex:
  (¬v_R ∨ ¬v_G) (¬v_R ∨ ¬v_B)
  (¬v_G ∨ ¬v_B)
for each edge (u, v), each colour c:
  (¬u_c ∨ ¬v_c)
```

A satisfying assignment *is* a colouring; "unsatisfiable" is a proof that none exists. A triangle is satisfiable; K4 (four mutually connected vertices) is not.

The same style encodes standard 9×9 Sudoku (729 variables, "cell (r, c) holds digit d"), timetabling, register allocation and bounded model checking ("can the circuit reach a bad state within k steps?"). The pairwise "at most one" clauses are quadratic in the number of options; for large domains, encodings with auxiliary variables keep it smaller.

## Why it is hard: NP-completeness

SAT has a crucial asymmetry.

- **Checking** a proposed assignment is fast: evaluate each clause, linear time.
- **Finding** one seems to need search, and the best known algorithms for general SAT take exponential time in the worst case.

NP is the class of decision problems whose yes instances have polynomial-length certificates verifiable in polynomial time. In 1971 Stephen Cook proved (and Leonid Levin independently, around the same time) that SAT is **NP-complete**: every problem in NP can be translated into SAT in polynomial time. A fast SAT algorithm would therefore give fast algorithms for every NP problem: scheduling, routing, protein folding models, breaking many cryptosystems. Whether one exists is the P vs NP question. The complexity module covers this properly.

### Where the line falls

Restricting clause shape changes everything.

| Variant | Clause shape | Complexity |
|---|---|---|
| 2-SAT | ≤ 2 literals each | linear time |
| Horn-SAT | ≤ 1 positive literal each | linear time |
| 3-SAT | ≤ 3 literals each | NP-complete |
| General CNF | any | NP-complete |

**2-SAT** is easy because a two-literal clause (a ∨ b) is two implications: ¬a → b and ¬b → a. Build a graph with those edges. First reject any empty clause and encode a unit clause a as (a ∨ a). For the remaining 2-SAT instance, unsatisfiability holds exactly when some x and ¬x lie in the same strongly connected component (each implies the other). Tarjan's or Kosaraju's algorithm finds the components in linear time.

**Horn clauses** such as (¬a ∨ ¬b ∨ c), i.e. (a ∧ b) → c, are rules. Begin with no variables derived true, propagate positive facts through rules, and report a conflict if an all-negative clause has all its variables forced true. With counters and occurrence lists this is linear in input size. Finite Datalog uses related fixed-point reasoning; general Prolog execution is not the same algorithm or termination guarantee.

Three literals per clause is enough for full hardness: any clause can be split into 3-literal clauses with fresh variables.

## DPLL: search with propagation

The classic algorithm, DPLL (Davis, Putnam, Logemann, Loveland, 1962), is backtracking search plus one crucial trick.

**Unit propagation**: if a clause has only one unassigned literal left and every other literal is false, that literal is forced. Setting it may force others, in a chain. If a clause ever has all literals false, that is a **conflict**: backtrack.

```python
def assign(cnf, lit):
    # drop satisfied clauses,
    # remove the falsified literal
    return [c - {-lit} for c in cnf
            if lit not in c]

def dpll(cnf, model=()):
    # unit propagation
    while True:
        if frozenset() in cnf:
            return None        # conflict
        if not cnf:
            return model       # all sat
        unit = next((c for c in cnf
                     if len(c) == 1), None)
        if unit is None:
            break
        (lit,) = unit
        cnf = assign(cnf, lit)
        model += (lit,)
    # branch on some literal
    lit = next(iter(cnf[0]))
    for choice in (lit, -lit):
        r = dpll(assign(cnf, choice),
                 model + (choice,))
        if r is not None:
            return r
    return None
```

Clauses are frozensets of nonzero integers, with −3 meaning ¬x3. Call dpll with its default empty model; a returned partial model satisfies all clauses and any omitted variables may be chosen freely. This recursive teaching solver is limited by runtime recursion and resource bounds. On the example formula from the CNF section it never branches at all:

```
start  {1,2} {-1,3} {-2,-3} {-3}
unit ¬x3: {1,2} {-1}
unit ¬x1: {2}
unit x2:  (no clauses left)
model: x3=F, x1=F, x2=T
```

The original DPLL also used **pure literal elimination**: if a variable appears with only one polarity, set it that way, since it can only help.

## CDCL: learning from mistakes

Modern solvers (MiniSat, Glucose, CaDiCaL, Kissat) use **conflict-driven clause learning**. The key ideas:

1. **Clause learning.** When propagation hits a conflict, analyse *which decisions* caused it, and add a new clause forbidding that combination. If deciding x1 = T and x7 = F always leads to a conflict, learn (¬x1 ∨ x7). While retained, the learned clause prevents propagation from accepting that same conflicting combination. Practical solvers can later delete learned clauses.
2. **Non-chronological backjumping.** Instead of undoing only the last decision, standard first-UIP analysis backjumps to the second-highest decision level among literals in its learned clause, or level zero for a unit clause, making that clause assert a literal. This need not be the earliest involved decision.
3. **Decision heuristics** such as VSIDS: prefer variables that have appeared in recent conflicts, so the search concentrates on the hard core of the problem.
4. **Restarts.** Periodically discard decisions while retaining root consequences and useful learned clauses (subject to clause deletion), to escape unlucky early decisions.
5. **Watched literals.** During ordinary propagation, nonunit clauses can watch two literals and avoid scans unless a watched literal becomes false. Unit clauses and other solver phases need separate handling.

These techniques do not provide a polynomial-time guarantee for general SAT. Standard complete search can still require exponential work; restarting and clause-deletion policies also affect progress. It is that real-world formulas have structure (modules, locality, near-independent parts), and CDCL exploits it. Runtime depends on encoding, solver, hardware and instance structure.

> [!note] Evidence gap
> Universal claims about million-clause solve times or millisecond verification are omitted: no reproducible benchmark set and machine configuration were supplied.

> [!note] What "unsatisfiable" means here
> Basic CDCL learns resolution consequences. Production solvers may also use preprocessing or stronger transformations, and can emit checkable proof logs such as DRAT. DRAT permits steps beyond ordinary resolution; an independently checked log reduces reliance on the solver, while still depending on the checker and input encoding. Exponential resolution lower bounds for standard pigeonhole encodings do not automatically establish the same limit for every extended solver or encoding.

## Hard and easy instances

Random-instance experiments must specify the clause distribution, number of variables and solver. Clause density can correlate with satisfiability and observed difficulty in such experiments; it does not determine whether an individual formula is easy. Industrial formulas have different structure.

> [!note] Evidence gap
> The previous universal density cutoff and easy/hard classifications are omitted because they conflated a model-dependent approximate threshold with a theorem and a runtime guarantee.

## Where SAT is used

- **Hardware verification**: equivalence checking and bounded model checking of chip designs, a major driver of solver research.
- **Package managers**: dependency resolution with version constraints is NP-complete in general. libsolv (used by openSUSE's zypper and Fedora's DNF) and SAT4J (in Eclipse's p2 installer) treat it as a SAT problem.
- **SMT solvers** (Satisfiability Modulo Theories) such as Z3 and cvc5 extend SAT with integers, arrays and bit-vectors. They are the engines inside Dafny, symbolic execution tools, and AWS's Zelkova, which reasons about IAM access policies.
- **Planning, scheduling and test generation**: encode "find a schedule" or "find an input reaching this branch" as constraints.

> [!tip] Using a solver in practice
> You rarely write DPLL yourself. Encode the problem, hand it to a solver (Python bindings exist for most), and spend your effort on the encoding. Sound symmetry-breaking constraints may reduce search. For unconstrained graph colouring with interchangeable colours, fixing one vertex to red preserves satisfiability; precolouring or other colour-specific constraints can invalidate that symmetry. Measure the effect on the actual workload.

## Key takeaways
- SAT asks whether some assignment makes a formula true; checking an answer is fast, finding one may take 2ⁿ steps.
- Solvers take CNF; the Tseitin transformation gives an equisatisfiable CNF of linear size.
- SAT and 3-SAT are NP-complete (Cook–Levin); 2-SAT and Horn-SAT are solvable in linear time.
- DPLL is backtracking plus unit propagation; CDCL adds clause learning, backjumping, VSIDS, restarts and watched literals.
- Worst-case hardness remains, but real-world structure makes SAT and SMT solvers practical for verification, dependency resolution and constraint solving.

## Further reading
- [Boolean satisfiability problem — Wikipedia](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
- [Conflict-driven clause learning — Wikipedia](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning)
- [DPLL algorithm — Wikipedia](https://en.wikipedia.org/wiki/DPLL_algorithm)
- [Tseytin transformation — Wikipedia](https://en.wikipedia.org/wiki/Tseytin_transformation)
- [2-satisfiability — Wikipedia](https://en.wikipedia.org/wiki/2-satisfiability)
- [Cook–Levin theorem — Wikipedia](https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem)
- [MiniSat](http://minisat.se/)
- [Z3 theorem prover — GitHub](https://github.com/Z3Prover/z3)
