---
id: cx-recursion-trees
sourceLesson: cx-recurrences
title: Adding up recursion trees
level: advanced
minutes: 2
summary: Sum level costs to identify whether roots, levels or leaves dominate.
---

A recursion tree turns recursive work into levels you can add. Each node is one call, labelled with only that call's outside work. Here n is the original input size; leaves have bounded positive cost.

## Three shapes explain many bounds

For two half-size children with linear outside work, each level processes the original input amount in total. More nodes are offset by smaller ranges. Halving produces logarithmically many levels, so total work is Θ(n log n).

```diagram
          whole
         /     \
       half    half
      /   \    /   \
   quarter quarter quarter quarter
```

This picture describes equal halves, not all possible recursion trees. For powers of two, the final level consists of n size-one leaves. Those base-case costs must be included in an exact count even though they do not change the linear-times-log bound.

With three half-size children and linear outside work, each level has one and a half times the previous level's work. A growing geometric series is controlled by its bottom levels, so the many constant-cost leaves dominate.

With two half-size children and quadratic outside work, each level has only half the previous level's work. A shrinking geometric series is controlled by its top levels, giving Θ(n²) total work.

## Depth alone is not total work

A single child on a fixed fraction of the input with constant outside work has logarithmic total cost. Changing from halves to thirds changes only a constant factor. Two half-size children with constant work per node instead create a linear number of nodes. A logarithmic depth does not imply a logarithmic total.

If one halving child does logarithmic outside work at each call, those contributions decrease gradually across the chain. Their sum is the square of a logarithm, not just one logarithm. Inspect work per level as well as depth.

## Key takeaways
- Add each level's whole cost, including base-case leaves.
- Equal level costs accumulate across the depth.
- Geometrically growing or shrinking levels favour leaves or root respectively.

## Further reading
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
