---
id: cx-loop-counting
sourceLesson: cx-analysing-code
title: Counting sequential and nested loops
level: intermediate
minutes: 4
summary: Add sequential work and count the true length of dependent inner loops.
---

You now have the notation. This lesson is about using it: looking at a piece of code and working out its time complexity quickly and correctly. Most code reduces to a handful of patterns, plus a few traps that catch even experienced engineers.

Throughout, n is the input size (for example the length of the list), and m is the size of a second input when there is one. O(...) is Big-O, an upper bound on growth; Θ(...) is Big-Theta, a tight bound; and logarithms use base two, roughly how many times you can halve n before reaching 1.

## The basic rules

1. **Cost model.** Treat fixed-size arithmetic, comparison and indexing as O(1). Python arbitrary-precision integers, long strings, user-defined comparisons and output can cost more; the counts below abstract those costs unless stated otherwise.
2. **Sequential blocks add.** A linear block followed by a quadratic block has quadratic overall growth, because the quadratic term dominates.
3. **Nested independent loops multiply.** O(n) iterations, each doing O(m) work, give O(nm), where n and m are the separate input sizes.
4. **Branches take the worse side.** For the worst case, choose the more expensive branch.
5. **Function calls cost whatever the function costs.** A one-line call to `sorted()` is O(n log n), where n is the list length.

Those cover simple code. The interesting cases are loops whose bounds change.

## Dependent nested loops

When the inner loop depends on the outer variable, you have to **sum** rather than multiply.

```python
# work() means one constant-cost step.
for i in range(n):
    # The inner loop's length depends on i.
    for j in range(i):
        work()
```

The inner loop lengths rise from zero to one less than the outer bound. Add those lengths:

```formula
W(n) = 0 + 1 + 2 + … + (n − 1)
W(n) = Σ_{i=0}^{n−1} i
W(n) = n(n − 1) / 2 = Θ(n^2)
W(10) = 10 × 9 / 2 = 45
where
W(n): the number of times work() runs
n: the input size, the bound of the outer loop
i: the outer loop's counter; on pass i the inner loop runs i times
Σ_{i=0}^{n−1}: capital sigma, "sum of": add up the expression after it for every whole number i from 0 to n − 1
…: "and so on" up to the last term
Θ(n^2): Big-Theta of n squared: grows at exactly the rate of n × n, up to a constant factor
In words: the inner loop runs once more on each pass, the runs add up to about half of n squared, and halving does not change the growth class.
```

Halving the work does not change the class.

Three nested loops over `i < j < k` do one step per triple of different positions:

```formula
W_3(n) = n(n − 1) × (n − 2) / 6
W_3(n) ≈ n^3 / 6 = Θ(n^3)
where
W_3(n): the number of steps the three nested loops take
n: the input size
≈: approximately equal to, for large n
Θ(n^3): Big-Theta of n cubed: grows at exactly the rate of n × n × n, up to a constant factor
In words: there are about a sixth of n cubed ways to choose three positions in order, which is still cubic.
```

> [!tip] A quick sanity check
> For nested loops, ask "roughly how many times does the innermost line run, as a fraction of the full box?" If it's a constant fraction (a half, a sixth), the class is the same as the full product.

## Key takeaways
- Sequential blocks add; independent nested counts multiply.
- When the inner bound depends on the outer variable, sum the actual counts.
- A function call contributes the work of its body, rather than a single free step.

## Further reading
- [TimeComplexity — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
