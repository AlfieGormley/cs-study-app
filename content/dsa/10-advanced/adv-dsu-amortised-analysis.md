---
id: adv-dsu-amortised-analysis
title: Understanding inverse-Ackermann bounds
level: intermediate
minutes: 4
summary: Initialisation and later operations have separate costs.
sourceLesson: adv-union-find
---

## How fast is it?

In this table n is the number of elements and m counts the complete sequence of finds and unions, including the unions that create any long path. Initialisation is charged separately. O(f) means "grows at most in proportion to f".

| Version | Cost per operation |
|---|---|
| Naive | O(n) worst case |
| Union by size or rank | O(log n) worst case |
| Path compression only | O(log n) amortised |
| Both | O(α(n)) amortised |

**α(n)** is the inverse Ackermann function. It grows so slowly that it is a tiny number for any practical input size. Its exact small value depends on the convention used to define it. You do not need an Ackermann table to choose or implement Union-Find.

The practical distinction is between a bound for one operation and a bound for a complete sequence. Balancing limits how long one root path can be; compression makes later traversals cheaper by repairing paths already visited.

“Amortised” matters: one `find` may still traverse a logarithmic path, then flatten it. Across m finds and unions on n initially separate elements, later work is O(m α(n)), plus O(n) to initialise the arrays. These bounds describe growth, not measured pointer counts. They include the operations that built the paths; do not start the analysis from an arbitrary uncharged tree.

> [!note] Rank after compression
> Path compression changes heights but never updates ranks. That is fine: rank was only ever an *upper bound* on height, but the inverse-Ackermann proof also uses rank-growth and node-count invariants, not just this upper bound.

## Key takeaways

- Initialisation and later operations have separate costs.
- Inverse-Ackermann bounds apply to a sequence, not a fixed operation-step count.

## Further reading
- [Disjoint-set unions — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
