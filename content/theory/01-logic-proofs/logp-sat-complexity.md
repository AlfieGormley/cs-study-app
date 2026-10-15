---
id: logp-sat-complexity
title: SAT hardness and tractable clause families
level: advanced
minutes: 3
sourceLesson: logp-sat
summary: Checking a proposed assignment is linear in the total literal occurrences.
---

## Why it is hard: NP-completeness

SAT has a crucial asymmetry.

- **Checking** a proposed assignment is fast: evaluate each clause, linear time.
- **Finding** one seems to need search, and the best known algorithms for general SAT take exponential time in the worst case.

NP is the class of decision problems whose yes instances have polynomial-length certificates verifiable in polynomial time. In 1971 Stephen Cook proved (and Leonid Levin independently, around the same time) that SAT is **NP-complete**: every problem in NP can be translated into SAT in polynomial time. A fast SAT algorithm would therefore give fast algorithms for every NP problem: scheduling, routing, protein folding models, breaking many cryptosystems. Whether one exists is the P vs NP question. The complexity module covers this properly.

### Where the line falls

Restricting clause shape changes everything.

| Variant | Clause shape | Complexity |
|---|---|---|
| 2-SAT | is at most 2 literals each | linear time |
| Horn-SAT | is at most 1 positive literal each | linear time |
| 3-SAT | is at most 3 literals each | NP-complete |
| General CNF | any | NP-complete |

**2-SAT** is easy because a two-literal clause is two implications:

```formula
(a ∨ b) ≡ (¬a → b) ≡ (¬b → a)
where
a, b: literals (a variable or its negation)
∨: OR
¬: NOT
→: implies: "if ... then ..."
≡: is logically equivalent to
In words: "a or b" means "if a is false, b must be true", and also "if b is false, a must be true".
```

Build a graph with those edges. First reject any empty clause and encode a unit clause a as (a or a). For the remaining 2-SAT instance, unsatisfiability holds exactly when some x and not x lie in the same strongly connected component (each implies the other). Tarjan's or Kosaraju's algorithm finds the components in linear time.

**Horn clauses**, with at most one positive (un-negated) literal, are rules:

```formula
(¬a ∨ ¬b ∨ c) ≡ (a ∧ b) → c
where
a, b, c: propositional variables
¬: NOT
∨: OR
∧: AND
→: implies
≡: is logically equivalent to
In words: "not a or not b or c" says the same as the rule "if a and b, then c".
```

Begin with no variables derived true, propagate positive facts through rules, and report a conflict if an all-negative clause has all its variables forced true. With counters and occurrence lists this is linear in input size. Finite Datalog uses related fixed-point reasoning; general Prolog execution is not the same algorithm or termination guarantee.

Three literals per clause is enough for full hardness: any clause can be split into 3-literal clauses with fresh variables.


## Key takeaways
- Checking a proposed assignment is linear in the total literal occurrences.
- General SAT and 3-SAT are NP-complete; 2-SAT and Horn-SAT admit linear-time algorithms.

## Further reading
- [CMU lecture: SAT solvers and DPLL](https://www.cs.cmu.edu/~15414/f18/2018/lectures/13-dpll.pdf)
- [DPLL algorithm — Wikipedia](https://en.wikipedia.org/wiki/DPLL_algorithm)
