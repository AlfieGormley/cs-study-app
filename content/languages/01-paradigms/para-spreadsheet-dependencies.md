---
id: para-spreadsheet-dependencies
title: Dataflow and spreadsheet dependencies
level: intermediate
minutes: 3
sourceLesson: para-logic-dataflow
summary: Dependency edges constrain a valid recalculation order.
---

A spreadsheet exposes data dependencies directly: each formula reads other cells. Those dependencies explain both recalculation order and circular-reference errors.

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

Because only dependencies constrain order, independent nodes can run in parallel automatically.

## Spreadsheets

Spreadsheets are a familiar example of dataflow-style dependencies. Each formula cell is a node; references are edges.

| Cell | Formula | Value |
|---|---|---|
| A1 | 5 | 5 |
| B1 | `=A1*3` | 15 |
| C1 | `=A1+B1` | 20 |

In an automatic, nonvolatile acyclic calculation, changing A1 causes dependent cells to be recalculated in dependency order (B1 before C1, since C1 depends on B1). A formula that depends on itself, directly or indirectly, makes the graph cyclic, which Excel normally reports as a **circular reference**; optional iterative calculation can handle intentionally circular models subject to its convergence settings.

```python
# Evaluate only after dependencies exist.
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

## Key takeaways
- Dependency edges constrain a valid recalculation order.
- Cycles require special semantics rather than ordinary topological evaluation.

## Further reading
- [Excel recalculation](https://learn.microsoft.com/en-us/office/client-developer/excel/excel-recalculation)
- [Python: topological sorting](https://docs.python.org/3/library/graphlib.html)
