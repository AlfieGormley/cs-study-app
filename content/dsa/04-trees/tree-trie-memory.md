---
id: tree-trie-memory
title: Child representations and trie memory
level: intermediate
minutes: 4
sourceLesson: tree-tries
summary: Child arrays reserve every alphabet position even when unused.
---

A character trie starts at an always-present root representing the empty prefix. Earlier units used Node.kids as a dictionary of character-to-child links and Node.end as the complete-word flag. Here L counts characters in the searched string or prefix and n counts stored keys. Dictionary child access is expected constant time, rather than a worst-case guarantee.

## The memory problem

Tries are fast but notoriously **memory-hungry**, because every character of every unshared suffix gets its own node, and each node carries overhead.

Common child representations differ in how much they reserve per node. An array of child pointers reserves one slot for every possible character, used or not: with 8-byte pointers, a node for lowercase English reserves 26 slots, 208 bytes, and a node for arbitrary bytes reserves 256 slots, 2 KiB (2,048 bytes), before any object header.

| Children as | Lookup | Memory per node |
|---|---|---|
| Array of 26 (or 256) pointers | O(1) index | 208 B (or 2 KiB) with 8-byte pointers, mostly empty |
| Hash map / dict | O(1) expected | Small, but high constant overhead |
| Sorted list | O(log σ) | Compact |

Here σ (sigma) is the alphabet size, and O(log σ) is the cost of a binary search among at most σ sorted children. A tree of N nodes has only N − 1 child links in total, so in a 26-slot array trie only about one slot in 26 ever holds a child, whatever the words are. Dictionary and node object sizes vary by language and interpreter build, so measure before choosing between the compact options.

> [!analogy] Real-world analogy: a rack of letter trays at every desk
> An office gives every desk a rack of 26 letter trays, one per letter of the alphabet, so post can be filed instantly. But most desks only ever receive post in one or two trays, and the racks take up more room than the post.
>
> **How it maps:** each desk is a trie node, each tray is a child-pointer slot, and post arriving is a child that actually exists. Instant filing is the O(1) array lookup; the empty trays are the wasted slots.
>
> **Where it stops:** an office could share racks between desks. A trie node's slots belong to that node alone, so the only cures are to store just the children that exist or to merge chains of single-child nodes.

With long mostly unshared suffixes, many nonterminal trie nodes have exactly one child: the unshared tail of a single word like `...ication`. That observation drives the fix.

## Why uniform hashes share little structure

SHA-256 values use 64 hexadecimal characters when encoded as hex. Imagine storing one million independent, approximately uniform hashes in a character trie. Each additional character multiplies the possible prefixes by sixteen, so the keys run out of company quickly:

- At depth 5 there are just over a million possible prefixes, about one per key, so many keys still share: only about 39 % have a 5-character prefix to themselves.
- By depth 7 there are 268 million possible prefixes, and about 99.6 % of keys are alone.
- From there to character 64, almost every key owns a private chain of single-child nodes.

Adding up the expected number of distinct prefixes at every depth gives about 60 million nodes for a million keys: roughly 60 nodes per key, each carrying its own child structure. A radix tree compresses those long private suffixes, but a hash set is usually the first structure to consider when the task needs only exact membership and no prefix queries.

## Key takeaways
- Child arrays reserve every alphabet position even when unused.
- Dictionary and object overhead depends on the implementation.
- Mostly unshared suffixes make character tries poor exact-match indexes.

## Further reading
- [Trie — Wikipedia](https://en.wikipedia.org/wiki/Trie)
- [Tries — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/52trie/)
