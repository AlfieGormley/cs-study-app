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

Common child representations differ in how much they reserve per node. An array of child pointers reserves one slot for every possible character, used or not:

```formula
M = σ p
M = 26 × 8 B = 208 B
M = 256 × 8 B = 2048 B = 2 KiB
where
M: the memory for one node's child-pointer array, in bytes (B), excluding object headers
σ: sigma, the alphabet size: the number of possible characters (26 lowercase English letters, or 256 possible byte values)
p: the size of one pointer, 8 bytes under an assumed 8-byte pointer representation
B: byte, 8 bits
KiB: kibibyte as used here, 1,024 bytes
In words: an array-of-pointers node costs one pointer for every letter of the alphabet, even though most nodes use only one or two of them.
```

| Children as | Lookup | Memory per node |
|---|---|---|
| Array of 26 (or 256) pointers | O(1) index | 208 B (or 2 KiB) with 8-byte pointers, mostly empty |
| Hash map / dict | O(1) expected | Small, but high constant overhead |
| Sorted list | O(log σ) | Compact |

O(log σ) is the cost of a binary search among at most σ sorted children. Dictionary and node object sizes vary by interpreter build.

> [!note] Evidence gap
> The claimed CPython dictionary sizes and 100,000-word, 65 MB benchmark are omitted because the pinned build, word list, measurement code and retained-object accounting were unavailable. No measured tenfold memory ratio is established.

With long mostly unshared suffixes, many nonterminal trie nodes have exactly one child: the unshared tail of a single word like `...ication`. That observation drives the fix.

## Why uniform hashes share little structure

SHA-256 values use 64 hexadecimal characters when encoded as hex. Imagine one million independent, approximately uniform hashes. Each additional character multiplies the possible prefixes by sixteen. At shallow depths many keys collide; farther down, almost every key owns its entire remaining suffix.

```formula
P_d = 16^d
q_d = (1 − 16^(−d))^(n − 1)
q_5 ≈ 0.385
q_7 ≈ 0.996
where
d: prefix depth in characters, from 1 to 64
P_d: number of possible hexadecimal prefixes at depth d
q_d: probability that one chosen key shares its depth-d prefix with no other stored key
n: number of independent uniform keys, here 1,000,000
q_5, q_7: that probability at depths five and seven
≈: approximately equal to, with probabilities rounded
In words: at depth five many keys still share prefixes, but by depth seven almost every key has a prefix to itself.
```

Counting occupied prefixes at each depth estimates the non-root node count:

```formula
M = Σ_d 16^d (1 − (1 − 16^(−d))^n)
M ≈ 59.68 × 10^6
where
M: expected number of non-root character-trie nodes
Σ_d: sum across all depths d from 1 to 64
d: prefix depth in characters
n: number of independent uniform keys, here 1,000,000
≈: approximately equal to, rounded to two decimal million nodes
In words: count a node wherever at least one key uses a prefix, then add those counts over all depths.
```

This model estimates about 59.68 million nodes, not bytes. Allocation overhead remains representation-dependent. A radix tree compresses the long private suffixes; a hash set is usually the first structure to consider when the task needs only exact membership and no prefix queries. Real hashes are modelled as approximately uniform here, rather than assumed to make every finite sample perfectly balanced.

## Key takeaways
- Child arrays reserve every alphabet position even when unused.
- Dictionary and object overhead depends on the implementation.
- Mostly unshared suffixes make character tries poor exact-match indexes.

## Further reading
- [Trie — Wikipedia](https://en.wikipedia.org/wiki/Trie)
- [Tries — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/52trie/)
