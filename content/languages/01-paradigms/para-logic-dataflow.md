---
id: para-logic-dataflow
title: Logic and dataflow languages
level: intermediate
minutes: 12
summary: Prolog's facts, rules, unification and backtracking, Datalog's comeback in code analysis, and dataflow from spreadsheets to reactive UIs.
---

Imperative, object-oriented and functional programming dominate everyday code, but two other paradigms quietly power a lot of software: **logic programming**, where you state facts and rules and ask questions, and **dataflow programming**, where a program is a graph through which values flow.

You may never write Prolog for a living. You almost certainly use spreadsheets, build systems, reactive UI frameworks and static analysers, all of which borrow these ideas.

## Logic programming

In logic programming, a program is a set of **facts** and **rules** in a form of logic. You run it by asking a **query**, and the system searches for values that make the query true.

**Prolog** (Alain Colmerauer and Philippe Roussel, Marseille, 1972) is the classic language. Here is a small family database:

```prolog
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z),
                  ancestor(Z, Y).
```

Read `:-` as "if" and `,` as "and". Variables start with a capital letter. The two rules say: X is an ancestor of Y if X is a parent of Y, *or* if X is a parent of some Z who is an ancestor of Y.

There is no function called `ancestor` that you call with inputs. You ask questions:

```prolog
?- ancestor(tom, ann).
true.

?- ancestor(tom, Who).
Who = bob ;
Who = ann ;
Who = pat.
```

The same relation answers "is Tom an ancestor of Ann?", "who are Tom's descendants?" and, with `ancestor(Who, pat)`, "who are Pat's ancestors?". Relations have no fixed inputs and outputs.

### Unification

Prolog matches queries against facts and rule heads by **unification**: finding values for variables that make two terms identical.

| Term 1 | Term 2 | Result |
|---|---|---|
| `f(X, b)` | `f(a, Y)` | X = a, Y = b |
| `f(X, X)` | `f(a, b)` | Fails |
| `[H\|T]` | `[1, 2, 3]` | H = 1, T = [2, 3] |

The `[H|T]` pattern splits a list into head and tail, much like pattern matching in Haskell, but unification works in both directions. That lets you run some predicates "backwards":

```prolog
?- append(X, Y, [1, 2]).
X = [],     Y = [1, 2] ;
X = [1],    Y = [2] ;
X = [1, 2], Y = [].
```

`append` was written to join lists, yet here it enumerates every way to *split* one.

### Backtracking search

Prolog answers a query by **depth-first search with backtracking** (formally, SLD resolution). It tries clauses top to bottom and goals left to right. When a goal fails, it backs up to the most recent choice and tries the next alternative.

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

### Closed world and negation

Prolog uses the **closed-world assumption**: a goal that finitely fails is treated as false for negation as failure. A search that loops has not established failure. Negation is **negation as failure**: `\+ parent(ann, _)` succeeds if Prolog *fails to find* any child of Ann. That is not the same as "Ann has no children" in classical logic; it means the goal finitely failed against the available facts and rules.

### Where logic programming lives today

- **Datalog** is a restricted logic language: no compound data terms and (in its basic form) every rule must be safe. For basic positive, function-free Datalog over a finite domain, bottom-up fixed-point evaluation terminates because only finitely many facts can be derived. Bottom-up evaluation is common, not the only strategy. Extensions such as arithmetic that generates new values can lose the finite-domain termination guarantee. GitHub's **CodeQL** query language is a Datalog descendant used to find security bugs; **Soufflé** runs Datalog static analyses of Java programs; **Datomic** queries are Datalog.
- **Policy engines**: Open Policy Agent's **Rego** language was inspired by Datalog.
- **SQL** recursive CTEs compute the same transitive closure as `ancestor`.
- **Constraint logic programming** (for example CLP(FD) in SWI-Prolog) solves scheduling and puzzles by stating constraints instead of search code.
- **Type checkers**: Rust's trait solver and Haskell's type class resolution are logic-programming engines internally.

## Dataflow programming

A **dataflow** program is a directed graph. Nodes are operations; edges carry values. A node runs when its inputs are available, and its outputs flow to downstream nodes. There is no program counter stepping through statements: order is determined by data dependencies alone.

```
  a ----> [*3] ---> b
  |                 |
  +-------> [+] <---+
             |
             v
             c
```

Because only dependencies constrain order, independent nodes can run **in parallel** automatically.

### Spreadsheets

Spreadsheets are a familiar example of dataflow-style dependencies. Each formula cell is a node; references are edges.

| Cell | Formula | Value |
|---|---|---|
| A1 | 5 | 5 |
| B1 | `=A1*3` | 15 |
| C1 | `=A1+B1` | 20 |

In an automatic, nonvolatile acyclic calculation, changing A1 causes dependent cells to be recalculated in dependency order (B1 before C1, since C1 depends on B1). A formula that depends on itself, directly or indirectly, makes the graph cyclic, which Excel normally reports as a **circular reference**; optional iterative calculation can handle intentionally circular models subject to its convergence settings.

```python
from graphlib import TopologicalSorter

deps = {"B1": {"A1"},
        "C1": {"A1", "B1"}}
formulas = {
    "B1": lambda v: v["A1"] * 3,
    "C1": lambda v: v["A1"] + v["B1"],
}
vals = {"A1": 5}
order = TopologicalSorter(deps)
for cell in order.static_order():
    if cell in formulas:
        vals[cell] = formulas[cell](vals)
print(vals)
# {'A1': 5, 'B1': 15, 'C1': 20}
```

A cyclic `deps` makes `TopologicalSorter` raise `CycleError`: the same check as a circular reference.

### Other dataflow systems

- **Unix pipes**: `cat log | grep ERROR | sort | uniq -c` is a linear dataflow graph; processes can run concurrently, but sort generally needs the complete input before producing globally sorted output.
- **Build systems**: Make, Bazel and others rebuild only targets downstream of changed files.
- **Visual languages**: LabVIEW (lab instruments) and Simulink (control systems) are programmed by wiring boxes together.
- **Synchronous dataflow**: Lustre and its industrial descendant SCADE are used for safety-critical avionics and rail software, where timing must be provable.
- **Data processing**: Apache Beam, Flink and Spark build dataflow graphs of transformations and distribute them across a cluster. TensorFlow 1.x had you build a graph first, then run it.

### Reactive programming

**Reactive** UI frameworks apply dataflow to user interfaces. In **signals**-based libraries (SolidJS, Preact Signals, Angular signals, Vue's refs), a value declares what it is computed from, and the runtime tracks dependencies and updates only what's affected.

```javascript
// Preact Signals-style API
const price = signal(10);
const qty = signal(3);
const total = computed(
  () => price.value * qty.value);
// total.value is 30
price.value = 12;
// total.value is now 36
```

A naive push-based implementation can suffer **glitches**. In the graph above, if `a` changes and `c` is recomputed before `b`, `c` briefly sees the new `a` with the old `b`: an inconsistent state that never "should" exist. Glitch-free systems either update in topological order or mark nodes dirty and recompute lazily on read.

## Trade-offs

| Paradigm | Strength | Weakness |
|---|---|---|
| Prolog | Search, rules | Hidden cost, loops |
| Basic finite-domain Datalog | Fixed-point termination | Extensions may lose guarantee |
| Dataflow | Parallel, incremental | Cycles, glitches |

Both paradigms shine when the problem *is* naturally a set of rules (permissions, type systems, code analysis) or a graph of dependent values (spreadsheets, builds, UIs), and are awkward for long sequential processes.

## Key takeaways
- Logic programs are facts plus rules; you run them by asking queries, and relations can be used in several directions.
- Prolog works by unification and depth-first backtracking; clause and goal order affect termination and performance.
- Prolog's negation is negation as failure under a closed-world assumption.
- Basic finite-domain Datalog supports terminating fixed-point evaluation; CodeQL, Soufflé and Datomic use related or extended languages whose restrictions must be checked separately.
- Dataflow programs are graphs where nodes fire when inputs arrive; spreadsheets, pipes, build systems and Beam/Flink are examples.
- Reactive signals are dataflow for UIs; glitch-free implementations maintain dependency consistency, for example through ordering or lazy recomputation.

## Further reading
- [Prolog — Wikipedia](https://en.wikipedia.org/wiki/Prolog)
- [Learn Prolog Now!](https://lpn.swi-prolog.org/lpnpage.php?pageid=online)
- [Datalog — Wikipedia](https://en.wikipedia.org/wiki/Datalog)
- [About CodeQL — GitHub docs](https://codeql.github.com/docs/codeql-overview/about-codeql/)
- [Dataflow programming — Wikipedia](https://en.wikipedia.org/wiki/Dataflow_programming)
- [graphlib — Python docs](https://docs.python.org/3/library/graphlib.html)
