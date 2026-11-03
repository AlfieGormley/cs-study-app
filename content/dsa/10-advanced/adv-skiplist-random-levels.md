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

Later sampling lessons go the other way: using randomness *as the output*. Picking k items uniformly from a stream of unknown length, and shuffling an array so every order is equally likely, both have short algorithms that are easy to get subtly wrong.

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

Every inserted key appears on the bottom level. Independent promotion draws decide whether it also appears on the next level, and then the next. With fair coins, about half the keys reach the second level and a quarter reach the third, on average. Those are expected proportions, not exact quotas.

Higher levels become progressively sparser. Search can pass many keys there, then refine its position on lower levels. Independence from insertion order is what protects the expected bound when keys arrive already sorted.

> [!analogy] Real-world analogy: Express and local trains
> An express service skips many stations; a local service reaches all of them.
>
> **How it maps:** Upper skip-list levels skip keys, while lower levels provide finer access. Search drops to a finer level before it would pass the target.
>
> **Where it stops:** Skip-list stops are chosen randomly and linked by key order. They are not scheduled routes, and random promotion gives expected rather than hard worst-case travel bounds.

## Key takeaways

- Expected costs average over the structure’s own random choices for a fixed independent input.
- Geometric promotion creates progressively sparser express lanes.

## Further reading
- [Skip Lists — William Pugh](https://drum.lib.umd.edu/bitstreams/17176ef8-8330-4a6c-8b75-4cd18c570bec/download)
- [Skip-list structure — Open Data Structures](https://opendatastructures.org/ods-python/4_1_Basic_Structure.html)
