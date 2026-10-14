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

The most intuitive method is to draw the tree of calls and add up the work at each level. For merge sort, T(n) = 2T(n/2) + n:

```
level 0:        n                 = n
             /     \
level 1:   n/2     n/2            = n
          /  \     /  \
level 2: n/4 n/4  n/4 n/4         = n
          ...
level k: 2^k nodes of n/2^k       = n
          ...
leaves:  n nodes of size 1        = n
```

Each level does n work in total, and the size halves at each level. Add the levels:

```formula
W_k = 2^k × (n / 2^k) = n
L = log_2(n) + 1
T(n) = L × n = Θ(n × log n)
where
W_k: the total work done on level k of the tree
k: the level number, 0 at the root
2^k: the number of calls on level k (it doubles each level)
n / 2^k: the input size of each call on level k
n: the input size of the original call
L: the number of levels, from size n down to size 1
log_2(n): the base-2 logarithm of n, the number of halvings from n to 1
T(n): the total running time
Θ: Big-Theta, a tight bound up to constant factors
log: logarithm (base 2 here; the base only changes a constant)
In words: every level does n work, and halving takes log_2(n) steps to reach size 1, so the total is about n log n.
```

For n = 1,024 that is 11 levels of 1,024 work each, about 11,000 steps. Total: **Θ(n log n)**.

Now try T(n) = 3T(n/2) + n (the shape of Karatsuba's multiplication algorithm). The work per level now changes from level to level:

```formula
W_k = 3^k × (n / 2^k) = n × (3/2)^k
leaves = 3^{log_2(n)} = n^{log_2(3)}
n^{log_2(3)} ≈ n^{1.585}
where
W_k: the total work on level k
k: the level number, 0 at the root
3^k: the number of calls on level k (it triples each level)
n / 2^k: the input size of each call on level k
(3/2)^k: k copies of 1.5 multiplied together
leaves: the number of calls at the bottom level, size 1
log_2(n): the base-2 logarithm of n, the depth of the tree
log_2(3): the base-2 logarithm of 3, about 1.585
n: the input size
≈: approximately equal to
In words: each level does 1.5 times the work of the level above, so the bottom level, with n^1.585 tiny calls, outweighs everything above it.
```

The second line uses the identity a^(log_b n) = n^(log_b a): both sides equal b to the power log_b(a) × log_b(n) (here b = 2 and a = 3). A *growing* geometric series is dominated by its **last** term, the leaves, so T(n) = Θ(n^(log_2 3)), an exponent of about 1.585.

And T(n) = 2T(n/2) + n^2:

```formula
W_k = 2^k × (n / 2^k)^2 = n^2 / 2^k
T(n) ≤ n^2 × (1 + 1/2 + 1/4 + …) = 2 × n^2
where
W_k: the total work on level k
k: the level number, 0 at the root
2^k: the number of calls on level k
n / 2^k: the input size of each call on level k
n^2: n squared, n × n, the root's own work
T(n): the total running time
…: "and so on", halving each time
≤: less than or equal to
In words: each level does half the work of the level above, so the whole tree costs less than twice the root.
```

The work *shrinks* by half per level. A shrinking geometric series is dominated by its **first** term, the root: T(n) = Θ(n^2).

These three behaviours are the whole idea behind the Master Theorem.

> [!tip] The three shapes
> - Work per level **shrinks** geometrically: the root dominates. T(n) = Θ(f(n)), where f(n) is the root's own work.
> - Work per level is **equal**: multiply one level by the number of levels, log n.
> - Work per level **grows** geometrically: the leaves dominate. T(n) = Θ(number of leaves).

## Key takeaways
- Count the work on each level, then add the levels.
- Equal level costs accumulate over the tree depth.
- Geometrically shrinking costs favour the root; growing costs favour the leaves.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Algorithms by Jeff Erickson, chapter 1: Recursion](https://jeffe.cs.illinois.edu/teaching/algorithms/)
