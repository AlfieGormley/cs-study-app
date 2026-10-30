---
id: graph-flow-residuals
title: Flow conservation and residual cancellation
level: advanced
minutes: 4
sourceLesson: graph-advanced
summary: Flow respects capacities and conservation at interior vertices.
---

The last units of this module cover three ideas that turn up in real systems and senior interviews: how much a network can carry (**max flow**), how to pair things up optimally (**graph matching**), and which single link or vertex would break a network if it failed (**bridges and articulation points**). This unit sets up the flow model and the residual graph, the idea every flow algorithm is built on.

## Network flow

### The model

A **flow network** is a directed graph where each edge has an **edge capacity**: the most it can carry, in litres per second, Gbit/s, lorries per day. There is a **source vertex** s where everything starts and a distinct **sink** t where it ends. Assume finite capacities. A **flow assignment** assigns an amount to each edge, obeying two rules:

```formula essential
0 ≤ f(u, v) ≤ c(u, v)
Σ_x f(x, v) = Σ_y f(v, y)
  for v ≠ s and v ≠ t
|f| = Σ_y f(s, y) − Σ_x f(x, s)
where
u, v: the start and end of an edge u→v
x: any vertex with an edge into v (or into s)
y: any vertex with an edge out of v (or out of s)
s: the source vertex
t: the sink vertex
c(u, v): the edge capacity of u→v, never negative
f(u, v): the flow sent along edge u→v
Σ_x, Σ_y: add up over every such vertex x or y
≠: is not equal to
|f|: the value of the flow: the net amount leaving s
≤: is at most
In words: each edge carries between nothing and its edge capacity (the **edge capacity constraint**); every vertex except s and t passes on exactly what it receives (**flow conservation** rule); and the flow's value is what leaves the source.
```

For example, a pipe with an edge capacity of 10 litres per second can carry 0 to 10, and a junction receiving 7 must send out 7. The **maximum flow** problem asks for the largest possible value.

```
s --10--> a ---4----> t
|         | \        ^
10        2  8       |
|         |   \      | 10
|         v     v    |
+---10--> b -9-> c --+
```

Edges: s→a 10, s→b 10, a→b 2, a→t 4, a→c 8, b→c 9, c→t 10. The maximum flow is **14**.

### Why greedy fails

The obvious approach: find any s→t path with unused edge capacity, push as much as you can, repeat. It can get stuck.

```
     s
    / \
   1   1
  v     v
  a -1-> b
  |      |
  1      1
  v      v
  t <----+
```

Edges s→a, s→b, a→b, a→t, b→t, each with edge capacity 1. If greedy first picks s→a→b→t, it uses up s→a and b→t. Now s→b leads only to b, whose exit is full. Greedy stops at 1, but the max is 2 (s→a→t and s→b→t).

### The residual graph

The fix is to allow **undoing** flow. The following card describes one original edge’s residual contributions, assuming no original opposite-direction edge. With antiparallel edges, add the contributions in each direction:

```formula essential
r(u, v) = c(u, v) − f(u, v)
r(v, u) = f(u, v)
where
u, v: the ends of an original edge u→v
c(u, v): its edge capacity
f(u, v): the flow it currently carries
r(u, v): this edge’s **forward residual** contribution: unused edge capacity on u→v; the displayed card assumes no original v→u edge
r(v, u): this edge’s **backward residual** contribution: how much u→v flow you may cancel along v→u
In words: you can push up to the unused edge capacity forwards, and you can push up to the current flow backwards, which undoes it.
```

For example, an edge with an edge capacity of 10 carrying 6 units has 4 units of forward residual and 6 units of backward residual. So:

- the **forward residual** u→v is the unused edge capacity;
- this edge contributes a **backward residual** on v→u equal to its flow, meaning “you may cancel up to that many units”. With an original antiparallel edge, aggregate residual capacity also includes that opposite edge’s unused edge capacity.

An **augmenting path** is any s→t path in this residual graph. In the example, after the bad first path, the residual has s→b (1), the backward edge b→a (1), and a→t (1). Pushing along s→b→a→t cancels the a→b flow and reroutes it, giving 2.

> [!analogy] Real-world analogy: cancelling a booked delivery
> A haulier books lorries one route at a time. After an early booking, a later request finds no free route, until the dispatcher notices that cancelling part of the earlier booking would let both deliveries go by different roads.
>
> **How it maps:** booked lorries are flow, a road's spare lorries are its forward residual, and "you may cancel up to what you booked" is the backward residual. An augmenting path that uses a backward edge is a plan that cancels part of an earlier booking and reroutes it.
>
> **Where it stops:** cancelling a real booking may cost money or time. In a flow network cancellation is free and only the final totals on each edge matter, so the algorithm can undo earlier choices as often as it needs.

## Key takeaways
- Flow respects capacities and conservation at interior vertices.
- Backward residual edges cancel a previous forward decision.
- Account for original antiparallel edges when aggregating residual capacities.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 6.4 Maximum flow](https://algs4.cs.princeton.edu/64maxflow/)
- [Ford–Fulkerson algorithm — Wikipedia](https://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm)
- [Edmonds–Karp — cp-algorithms](https://cp-algorithms.com/graph/edmonds_karp.html)
