---
id: adv-skiplist-random-levels
title: Randomised guarantees and skip-list levels
level: advanced
minutes: 4
summary: Expected costs average over the structure’s own random choices for a fixed independent input.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

Balanced binary search trees such as red–black and AVL trees guarantee O(log n) operations (time growing in proportion to the logarithm of n, the number of keys stored), but their rebalancing rules are fiddly to get right. **Randomised structures** take another route: make a few random choices, and the structure is balanced *with high probability*, whatever order the keys arrive in.

The second half of this lesson goes the other way: using randomness *as the output*. Picking k items uniformly from a stream of unknown length, and shuffling an array so every order is equally likely, both have short algorithms that are easy to get subtly wrong.

## Expected vs worst case

A randomised structure's bounds are over its own independent random draws, not over the input. For any fixed input sequence independent of the random choices, suitably random priorities or promotion levels give expected logarithmic bounds. This is not a worst-case guarantee against every adaptive adversary. You would need to be unlucky, and the probability of being much slower than O(log n), where n is the number of keys, shrinks very quickly as n grows.

That is a stronger guarantee than "average case over random inputs", which a plain BST also has, and which sorted input breaks.

## Skip lists

A sorted linked list of n nodes has O(n) search, because you can only walk forward one node at a time. A **skip list**, introduced by William Pugh in 1990, adds **express lanes**: extra levels of linked lists, each containing a random subset of the level below.

```
L3: H ------------------> 30 ---------> None
L2: H ------> 10 -------> 30 ---------> None
L1: H -> 5 -> 10 -> 20 -> 30 -> 40 ---> None
```

When a key is inserted, it gets level 1, then flips a coin: heads, also join level 2; heads again, level 3; and so on. The chance of heads is called the promotion probability. Three numbers follow from it:

```formula
P(ℓ ≥ m) = p^{m − 1}
E[ℓ] = 1 / (1 − p)
H ≈ log_{1/p}(n)
P(ℓ ≥ 3) = (1/2)^2 = 1/4
E[ℓ] = 1 / (1 − 1/2) = 2
H ≈ log_2(1,000,000) ≈ 20
where
ℓ: the level a newly inserted key ends up with (1, 2, 3, …)
m: any level number we ask about
p: the promotion probability, strictly between zero and one; the chance of heads on each flip; 1/2 in the example, 1/4 in Redis
P(ℓ ≥ m): the probability that the key reaches level m or higher
p^{m − 1}: m − 1 copies of p multiplied together, one factor per heads needed
E[ℓ]: the expected (long-run average) level of a key
H: a large-n estimate of the whole list’s maximum occupied level, ignoring additive constants and a finite cap
n: the positive number of keys in the skip list
log_{1/p}(n): the logarithm of n to base 1/p: how many times you can divide n by 1/p before reaching 1
log_2(n): the base-2 logarithm of n, the special case p = 1/2
≥: is at least
≈: approximately equal to
In words: each extra level needs one more heads, so levels thin out geometrically; an average key sits on 2 levels at p = 1/2, and the tallest towers reach about log_2(n) levels.
```

So with a million keys and fair coins, about half the nodes reach level 2, a quarter level 3, and the list is about 20 levels tall. These are averages over the independent random draws; any single run can be a little taller or shorter.

## Key takeaways

- Expected costs average over the structure’s own random choices for a fixed independent input.
- Geometric promotion creates progressively sparser express lanes.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
- [Pugh’s Skip List Cookbook](https://drum.lib.umd.edu/bitstreams/17176ef8-8330-4a6c-8b75-4cd18c570bec/download)
