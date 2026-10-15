---
id: para-prolog-search
title: Backtracking, order and finite failure
level: intermediate
minutes: 3
sourceLesson: para-logic-dataflow
summary: Ordinary untabled Prolog tries clauses and goals in a defined search order.
---

A set of logical rules also needs an execution strategy. Ordinary untabled Prolog's search order determines which answers appear and whether the search reaches them.

## Backtracking search

Prolog answers a query by **depth-first search with backtracking** (using SLD resolution with this particular search strategy). It tries clauses top to bottom and goals left to right. When a goal fails, it backtracks to the most recent choice and tries the next alternative.

```
?- ancestor(tom, W)
 |- clause 1: parent(tom, W)
 |    W = bob             (answer 1)
 |- clause 2: parent(tom, Z), Z = bob
      ancestor(bob, W)
       |- clause 1: parent(bob, W)
       |    W = ann        (answer 2)
       |    W = pat        (answer 3)
       |- clause 2: ... no more
```

This makes Prolog declarative in *meaning* but procedural in *behaviour*. Clause order and goal order matter:

> [!warning] Left recursion loops
> Write the recursive rule as `ancestor(X, Y) :- ancestor(X, Z), parent(Z, Y).` and put it first, and a query like `ancestor(tom, W)` calls `ancestor(tom, Z)`, which calls `ancestor(tom, Z2)`, forever, until the stack runs out. Logically it is the same rule. Operationally it never reaches a fact.

## Closed world and negation

Prolog uses the **closed-world assumption**: a goal that finitely fails is treated as false for negation as failure. A search that loops has not established failure. Negation is **negation as failure**: `\+ parent(ann, _)` succeeds if Prolog *fails to find* any child of Ann. That is not the same as "Ann has no children" in classical logic; it means the goal finitely failed against the available facts and rules.

## Key takeaways
- Ordinary untabled Prolog tries clauses and goals in a defined search order.
- Negation as failure requires finite failure; looping is no proof of absence.

## Further reading
- [SWI-Prolog: tabling](https://www.swi-prolog.org/pldoc/man?section=tabling)
- [SWI-Prolog: negation as failure](https://www.swi-prolog.org/pldoc/doc_for?object=(%5C%2B)/1)
