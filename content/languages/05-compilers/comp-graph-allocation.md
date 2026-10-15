---
id: comp-graph-allocation
title: "Data-flow liveness and graph-colouring allocation"
level: advanced
minutes: 5
sourceLesson: comp-codegen-regalloc
summary: "Solve block liveness to a fixed point before constructing interference."
---

## Graph colouring

Once code has branches and loops, exact live regions need not be simple intervals: a value can be live in one branch and dead in another. Liveness is then computed for each basic block with the standard data-flow equations:

```formula
L_out(B) = ∪ L_in(S)   for all S in succ(B)
L_in(B) = use(B) ∪ (L_out(B) − def(B))
where
B: a basic block: a straight-line run of instructions with one entry and one exit
L_out(B): the set of values live as control leaves B
L_in(B): the set of values live as control enters B
S: a successor of B: a block that control can go to straight after B
succ(B): the set of B's successors
use(B): the values B reads before it assigns them
def(B): the values B assigns
∪: union: everything that is in either set
−: set difference: the left set with the members of the right set removed
In words: a value is live leaving a block if any block that can come next needs it, and live entering a block if the block reads it, or if it is live leaving and the block does not overwrite it.
```

The equations are solved by repeating them over every block until no set changes (a fixed point); loops are why more than one round can be needed. For example, if `x` is read only in the `then` branch of an `if`, it is in L_in(then) but not in L_in(else), and it is in L_out of the block before the branch, because one of its successors needs it.

The classic general approach (Chaitin, 1981) builds an **interference graph** with a node per value and an edge between any two values that are live at the same time. Allocating k registers is then **k-colouring** the graph so that no edge joins two nodes of the same colour:

```formula
c(u) ≠ c(v)   for all (u, v) ∈ E
c(v) ∈ {1, 2, …, k}
where
c: the colouring: c(v) is the register (colour) given to value v
u: a value, which is a node of the interference graph
v: another value, joined to u by an edge
E: the set of edges: pairs of values that are live at the same time
k: the number of available registers
≠: is not equal to
∈: is a member of
{ }: curly braces list the members of a set
…: "and so on" up to k
In words: every value gets one of the k registers, and two values that are live at the same time never get the same one.
```

```
  a ── b         k = 2: impossible,
  │ ╲  │         a, b, d form a
  │  ╲ │         triangle
  c    d
```

General k-colourability for k at least 3 is NP-complete, so register allocators use Chaitin's heuristic: repeatedly remove a node with fewer than k neighbours (it can always be coloured later), pushing it on a stack. The removal test is:

```formula
deg(v) < k
where
deg(v): the degree of node v: how many neighbours (interfering values) it still has in the graph
v: the node being considered for removal
k: the number of registers
<: is less than
In words: a node with fewer neighbours than there are registers is safe to set aside: even if every neighbour takes a different register, at least one is left over for it.
```

If every node has k or more neighbours, choose one to spill. Then pop nodes and give each a colour its neighbours do not use. Briggs' refinement (1994) defers the spill decision, because a node with k neighbours may still be colourable if two neighbours share a colour.

**Coalescing** is the other half: if the IR says `b = a`, assigning compatible noninterfering values the same register removes the copy. Conservative coalescing also checks whether merging could make allocation harder. This can remove copies introduced when leaving SSA; the outcome depends on interference and target constraints.

| Approach | Design emphasis |
|---|---|
| Linear scan | Interval processing with low allocation overhead |
| Graph colouring | Interference graph and colouring heuristics |
| LLVM greedy | Cost-driven splitting and reassignment |

Many JIT compilers use linear-scan algorithms to keep compilation latency low; HotSpot C1 and V8 provide examples. HotSpot C2 instead uses graph colouring. AOT and JIT compilers both balance compilation cost, generated-code quality and workload needs.

## Key takeaways
- Solve block liveness to a fixed point before constructing interference.
- Optimistic colouring delays spill decisions; conservative coalescing controls graph difficulty.

## Further reading
- [LLVM code generator design](https://llvm.org/docs/CodeGenerator.html)
- [Linear scan register allocation — Poletto and Sarkar](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Register allocation and coalescing research](https://www.cs.princeton.edu/~appel/modern/text/color1.html)
- [C11 committee draft: expressions and integer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [AArch64 procedure-call standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [Improvements to graph colouring register allocation — Briggs, Cooper and Torczon](https://rsim.cs.illinois.edu/arch/qual_papers/compilers/briggs94.pdf)
