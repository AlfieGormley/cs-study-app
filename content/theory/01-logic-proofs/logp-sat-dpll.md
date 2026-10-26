---
id: logp-sat-dpll
title: DPLL and forced assignments
level: advanced
minutes: 3
sourceLesson: logp-sat
summary: Unit propagation forces a literal when all other literals in its clause are false.
---

## DPLL: search with propagation

The classic algorithm, DPLL (Davis, Putnam, Logemann, Loveland, 1962), is backtracking search plus one crucial trick.

**Unit propagation**: if a clause has only one unassigned literal left and every other literal is false, that literal is forced. Setting it may force others, in a chain. If a clause ever has all literals false, that is a **SAT conflict**: backtrack.

The input is a list of clauses represented by Python `frozenset` objects containing nonzero integers that may be positive or negative. Positive integers are variables and negative integers negate those variables. These function definitions alone print nothing.

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
        # Record the forced signed literal.
        model += (lit,)
    # branch on some literal
    lit = next(iter(cnf[0]))
    # Explore each polarity if needed.
    for choice in (lit, -lit):
        r = dpll(assign(cnf, choice),
                 model + (choice,))
        if r is not None:
            return r
    return None
```

Clauses are frozensets of nonzero integers, with −3 meaning not x3. Call dpll with its default empty model; a returned partial model satisfies all clauses and any omitted variables may be chosen freely. This recursive teaching solver is limited by runtime recursion and resource bounds. On the earlier four-clause formula, over variables numbered 1, 2 and 3, it never branches at all. In the trace, each {…} is a clause, a number k stands for the variable xₖ and −k for its negation ¬xₖ (so {1,2} is x1 or x2), and in the model T means true and F false:

```
start  {1,2} {-1,3} {-2,-3} {-3}
unit ¬x3: {1,2} {-1}
unit ¬x1: {2}
unit x2:  (no clauses left)
model: x3 x1 x2
       F  F  T
```

The original DPLL also used **pure literal elimination**: if a variable appears with only one polarity, set it that way, since it can only help.


## Key takeaways
- Unit propagation forces a literal when all other literals in its clause are false.
- DPLL propagates, branches and backtracks; an empty clause is a conflict and an empty conjunction is satisfied.

## Further reading
- [CMU lecture: SAT solvers and DPLL](https://www.cs.cmu.edu/~15414/f18/2018/lectures/13-dpll.pdf)
- [Tseytin transformation — Wikipedia](https://en.wikipedia.org/wiki/Tseytin_transformation)
