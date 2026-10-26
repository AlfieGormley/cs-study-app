---
id: cx-loop-counting
sourceLesson: cx-analysing-code
title: Counting sequential and nested loops
level: intermediate
minutes: 2
summary: Add sequential work and count the true length of dependent inner loops.
---

Count how many times the meaningful operation runs, not how many loops are visible. Here n and m are independent input sizes. Assume each counted operation has constant cost.

## Add sequential work; multiply independent nested work

A list scan followed by a square-grid scan adds the two workloads. If n is list length and m is the grid's side length, the result is O(n + m²). Without a relationship between the list and grid sizes, neither contribution can be discarded.

A loop that restarts a full inner loop on every pass multiplies the two counts. A fixed inner bound, such as a hundred checks, changes the coefficient but leaves a full outer scan linear.

## Dependent bounds need a sum

```python
# n is the nonnegative input bound.
for i in range(n):
    # Earlier positions only.
    for j in range(i):
        work()
```

Here `work()` stands for one constant-cost operation. The inner lengths grow from zero to one less than the outer bound. Their total is roughly half a full square, so the work is Θ(n²). Halving a quadratic amount does not make it linear.

For a direct growth argument, the final half of outer passes each do at least about half the maximum inner work. That already gives a quadratic lower bound; the full square supplies a quadratic upper bound. No exact sum is needed.

Three ordered distinct positions similarly occupy a fixed fraction of a full cube, giving cubic growth. But nesting alone proves nothing: different dependent ranges can produce linear or logarithmic totals.

## Include hidden work

A function call costs its body, not one step. `sorted()` does comparisons and moves elements. Printing can format values and wait for output. State explicitly when counting calls instead of their elapsed costs. For a worst-case branch, analyse the most expensive path that a valid input can actually reach.

## Key takeaways
- Sequential phases add; independently repeated phases multiply.
- Sum actual inner lengths when bounds depend on the outer position.
- Count the work inside calls and state the cost model.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
