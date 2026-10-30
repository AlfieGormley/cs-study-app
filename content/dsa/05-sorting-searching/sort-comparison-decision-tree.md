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
3. Put the two together: the tree must be tall enough to have a leaf for every ordering.

```formula essential
2^h ≥ n!
h ≥ log_2(n!)
where
h: the height of the decision tree, which is the worst-case number of comparisons
n: the number of elements being sorted
n!: n factorial, n × (n − 1) × … × 2 × 1: the number of possible orderings of n distinct elements
2^h: 2 multiplied by itself h times: the most leaves a binary tree of height h can have
log_2: the base-2 logarithm, which undoes "2 to the power": log_2(8) = 3
≥: greater than or equal to
In words: h yes/no comparisons can tell apart at most 2^h orderings, so any comparison sort must make at least log_2(n!) comparisons on some input.
```

For three elements there are 6 orderings. Two comparisons can tell apart at most 4 cases, so some input needs 3, exactly what the tree above uses.

How big is that bound for large n? Throw away the smaller half of the factors in n factorial and shrink each of the rest down to half the input size: what is left is still a product of about n/2 factors, each about n/2. Its logarithm grows like n log n, so **every comparison sort needs Ω(n log n) comparisons in the worst case**.

```formula reference
n! ≥ (n / 2)^{n/2}
log_2(n!) ≥ (n / 2) log_2(n / 2)
log_2(n!) = Ω(n log(n))
where
n!: n factorial, the product n × (n − 1) × … × 1
n: the positive integer input size; the displayed half-factor step assumes even n of at least two (odd sizes change only the rounding)
(n / 2)^{n/2}: n/2 copies of n/2 multiplied together
log_2: the base-2 logarithm
log: the logarithm (the base does not matter inside Ω)
Ω: Big Omega: grows at least this fast, up to a constant factor
≥: greater than or equal to
In words: throwing away the smaller half of the factors and shrinking the rest to half the input size still leaves something whose logarithm grows like n log n.
```

> [!analogy] Real-world analogy: twenty questions
> In the game of twenty questions, one player thinks of something and the other may only ask yes/no questions. Each answer can at best rule out half of the remaining possibilities, so twenty questions can tell apart at most about a million things. If there are more possibilities than that, some secret cannot be pinned down in twenty questions, however clever the questioner.
>
> **How it maps:** the secret is the input's ordering (one of n factorial), each question is a comparison such as "is `a[i] < a[j]`?", and the number of questions needed in the worst case is the decision tree's height. Running out of questions before the possibilities are narrowed to one is a sort that gets some input wrong.
>
> **Where it stops:** a lucky guess can win the game early, and a sort can also finish early on some inputs, which the worst-case bound allows. And the bound covers only yes/no questions: an algorithm that asks "which of 256 buckets does this key's first byte pick?" gets far more than one bit per step, which is how counting and radix sort escape it.

## Key takeaways
- Distinct permutations require separate leaves and a worst-case logarithmic-height decision tree.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
