---
id: cx-recursion-trees
sourceLesson: cx-recurrences
title: Adding up recursion trees
level: advanced
minutes: 5
summary: Sum level costs to identify whether roots, levels or leaves dominate.
---

Here n is the original input size. For the exact counts below, take n to be a power of two and use a base-case cost of one at size one. Any fixed positive base-case cost gives the same asymptotic bounds. A recursion tree makes the distribution of work across levels visible.

## The recursion tree

The most intuitive method is to draw the tree of calls and add up the work at each level. For merge sort, two half-size calls are followed by a linear merge:

```
level 0:       whole         same total
             /     \
level 1:   half    half      same total
          /  \     /  \
level 2: 1/4 1/4  1/4 1/4   same total
          ...
each level: more nodes, smaller inputs
          ...
leaves: one-item nodes       same total
```

Each level does n work in total, and the size halves at each level. Add the levels:

```formula
W_k = 2^k × (n / 2^k) = n
N_k = 2^k, s_k = n / 2^k
N_leaf = n
L = log_2(n) + 1
T(n) = Ln = Θ(n log(n))
T(n) = 2T(n/2) + n
where
W_k: the total work done on level k of the tree
N_k: the node count on level k
s_k: the item count in each level-k node
N_leaf: the number of one-item leaf calls
k: the level number, 0 at the root
n: the input size of the original call
L: the number of levels, from size n down to size 1
log_2(n): the base-2 logarithm of n, the number of halvings from n to 1
T(n): the total running time
Θ: Big-Theta, a tight bound up to constant factors
log: logarithm (base 2 here; the base only changes a constant)
In words: every level does n work, and halving takes log_2(n) steps to reach size 1, so the total is about n log n.
```

For an input of 1,024 that is 11 levels of 1,024 work each, about 11,000 steps. Total: **Θ(n log n)**.

Now try three half-size calls plus linear outside work, the shape of Karatsuba multiplication. Level work changes as shown below:

```formula
W_k = 3^k × (n / 2^k) = n × (3/2)^k
leaves = 3^{log_2(n)} = n^{log_2(3)}
n^{log_2(3)} ≈ n^{1.585}
a^{log_b(n)} = n^{log_b(a)}
a = 3, b = 2
T(n) = Θ(n^{log_2(3)})
T(n) = 3T(n/2) + n
where
W_k: the total work on level k
k: the level number, 0 at the root
leaves: the number of calls at the bottom level, size 1
log_2(n): the base-2 logarithm of n, the depth of the tree
log_2(3): the base-2 logarithm of 3, about 1.585
n: the input size
≈: approximately equal to
a: the branching factor in the identity
b: the split factor and logarithm base, greater than one
log_b: logarithm to base b
log_b(a): the critical exponent
T(n): the running time on the original input
Θ: a tight growth bound
In words: each level does 1.5 times the work of the level above, so the bottom level, with n^1.585 tiny calls, outweighs everything above it.
```

The second line exchanges the roles of logarithm base and exponent in the identity shown in the card. Here branching uses three children and splitting halves each input. A growing geometric series is dominated by its **last** term, so leaf growth determines the cost.

Now take two half-size calls with quadratic outside work:

```formula
W_k = 2^k × (n / 2^k)^2 = n^2 / 2^k
T(n) ≤ n^2 × (1 + 1/2 + 1/4 + …) = 2n^2
T(n) = 2T(n/2) + n^2
where
W_k: the total work on level k
k: the level number, 0 at the root
T(n): the total running time
…: "and so on", halving each time
n: the original input size, a positive power of two in the exact counts here
≤: less than or equal to
In words: each level does half the work of the level above, so the whole tree costs less than twice the root.
```

The work *shrinks* by half per level. A shrinking geometric series is dominated by its **first** term, the root, giving Θ(n^2) work, where n is the original size.

These three behaviours are the whole idea behind the Master Theorem.

> [!tip] The three shapes
> - Work per level **shrinks** geometrically: the root dominates, so total work has the same tight growth as the root’s own work.
> - Work per level is **equal**: multiply one level’s work by the logarithmic number of levels.
> - Work per level **grows** geometrically: the leaves dominate, so total work has the same tight growth as the leaf count (with constant-cost leaves).

## Key takeaways
- Count the work on each level, then add the levels.
- Equal level costs accumulate over the tree depth.
- Geometrically shrinking costs favour the root; growing costs favour the leaves.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Algorithms by Jeff Erickson, chapter 1: Recursion](https://jeffe.cs.illinois.edu/teaching/algorithms/)
