---
id: sort-comparison-decision-tree
title: The comparison-sorting decision tree
level: intermediate
minutes: 4
sourceLesson: sort-heapsort-lower-bound
summary: Each distinct-key ordering needs a distinguishable decision-tree leaf.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## The lower bound for comparison sorts

Merge sort, heapsort and good quicksorts are all linear times logarithmic growth. Is that a coincidence of the algorithms we happened to find, or a law?

It is a law, for **comparison sorts**: algorithms that learn about the input only by asking "is `a[i] < a[j]`?". That includes every sort so far.

### The decision tree

Model any comparison sort on inputs of size n as a binary tree:

- Each internal node is a comparison, such as `a[1] < a[2]?`.
- Each branch is an answer (yes or no).
- Each leaf is a final answer: the permutation that sorts the input.

Running the algorithm on a particular input traces one path from root to leaf. The number of comparisons is the length of that path.

Here is a decision tree for sorting three elements `a, b, c`:

```
              a<b?
          yes/    \no
         b<c?      a<c?
       y/   \n    y/   \n
    a,b,c  a<c?  b,a,c  b<c?
          y/  \n       y/  \n
       a,c,b c,a,b  b,c,a  c,b,a
```

Six leaves, one per ordering. The worst-case path has 3 comparisons.

### The counting argument

1. There are **n!** (n factorial: n × (n − 1) × … × 2 × 1) possible orderings of n distinct elements. The algorithm must be able to output each one, so the tree needs **at least n! leaves**. (If two orderings led to the same leaf, the algorithm would rearrange them identically and get one of them wrong.)
2. A binary tree of height h (its longest root-to-leaf path) has **at most 2ʰ leaves**, because the number of nodes can at most double at each level.
3. Put the two together:

```formula
2^h ≥ L ≥ n!
h ≥ log_2(n!)
log_2(3!) = log_2(6) ≈ 2.58
h ≥ ⌈2.58⌉ = 3
where
h: the height of the decision tree, which is the worst-case number of comparisons; a whole number
L: the number of leaves in the tree
n!: n factorial, n × (n − 1) × … × 2 × 1: the number of possible orderings of n distinct elements (3! = 6)
2^h: h copies of 2 multiplied together, the most leaves a binary tree of height h can have
log_2: the base-2 logarithm, which undoes "2 to the power": log_2(8) = 3
n: the number of elements being sorted; 3 in the example lines
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
≈: approximately equal to
In words: a tree tall enough to hold one leaf per possible ordering must have height at least log_2(n!), so some input needs that many comparisons.
```

For three elements that is 3 comparisons, exactly what the tree above uses. The height is the worst-case number of comparisons, so this is the bound. Now estimate log₂(n!). For even input sizes, the largest half of the factorial’s factors are each at least half the input size. Odd sizes change only the rounding, preserving the asymptotic bound:

```formula
n! ≥ (n / 2)^{n/2}
log_2(n!) ≥ (n / 2) log_2(n / 2)
log_2(n!) = Ω(n log(n))
where
n!: n factorial, the product n × (n − 1) × … × 1
n: the positive integer input size; assume even n of at least two for the displayed half-factor derivation
(n / 2)^{n/2}: n/2 copies of n/2 multiplied together
log_2: the base-2 logarithm
log: the logarithm (the base does not matter inside Ω)
Ω: Big Omega: grows at least this fast, up to a constant factor
≥: greater than or equal to
In words: throwing away the smaller half of the factors and shrinking the rest to n/2 still leaves something that grows like n log n.
```

## Key takeaways
- Distinct permutations require separate leaves and a worst-case logarithmic-height decision tree.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
