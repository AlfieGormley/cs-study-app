---
id: dist-merkle-background-repair
title: Merkle trees and safe background repair
level: intermediate
minutes: 4
summary: Locate differing replica ranges efficiently and prevent deleted data from being resurrected.
sourceLesson: dist-quorums
---

Read repair only touches keys that clients read. Anti-entropy compares replicas in the background, using hashes to avoid sending every key merely to discover which ranges differ.

## Anti-entropy with Merkle trees

Anti-entropy compares replicas in the background and copies missing data. Comparing every key over the network would be enormous, so Dynamo uses **Merkle trees** (hash trees).

Each replica builds a tree over a key range. Leaves hash small sub-ranges of keys; each internal node hashes its child hashes.

```
          root
        /      \
     h12        h34
    /   \      /   \
  h1    h2   h3    h4
 keys  keys keys  keys
 0-24 25-49 50-74 75-99
```

Two replicas compare roots. If they're equal, treat the range as identical, assuming consistent tree construction and no hash collision: done in one hash comparison. If not, compare the children and recurse only into subtrees that differ.

> [!example] How much does it save?
> 1 billion keys, leaves of ~1,000 keys, so ~1 million leaves and a tree depth of 20. If one key differs, replicas exchange about 2 hashes per level × 20 levels = 40 hashes, then sync one leaf range of 1,000 keys, instead of comparing a billion.

The saving comes from the tree's depth. A binary tree (each parent has two children) halves the range at every level, so its depth is the base-2 logarithm of the number of leaves:

```formula
B = K / k = 10^9 / 10^3 = 10^6
d = log_2(B) = log_2(10^6) ≈ 20
H ≈ 2 × d = 2 × 20 = 40
where
K: the total number of keys; here 1 billion (10^9)
k: the number of keys under each leaf; here 1,000 (10^3)
B: the number of leaves (buckets of keys); here 1 million (10^6)
d: the depth of the tree, the number of levels from root to leaf
log_2: the base-2 logarithm: how many times you can halve a number before reaching 1; log_2(1,024) = 10
H: the number of hashes exchanged to find one differing leaf
≈: approximately equal to
In words: each level down halves the range to search, so finding one bad leaf among a million takes about 20 steps of 2 hash comparisons each.
```

This best case assumes only one leaf differs. If many keys differ, spread across many leaves, the replicas must descend into many subtrees and can end up comparing most of the tree.

Costs: trees must be rebuilt or updated when data changes, and recalculated when nodes join or leave (key ranges shift). Cassandra's `nodetool repair` builds Merkle trees per token range; operators must run it at least every `gc_grace_seconds` (10 days by default), otherwise deleted data can be **resurrected** when a replica that missed a tombstone reintroduces the old value after the tombstone is purged.

## Putting it together

| Mechanism | Fixes | When |
|---|---|---|
| Hinted handoff | Writes missed by down nodes | On recovery |
| Read repair | Stale replicas of hot keys | On read |
| Anti-entropy | Everything else | Background |

## Key takeaways
- Merkle roots let matching ranges be skipped; only differing subtrees need deeper comparison.
- One differing leaf gives logarithmic tree descent, while many scattered differences can require much more work.
- Repair must cover missed deletes before tombstones are purged, or old data can return.

## Further reading
- [Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Cassandra repair](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/repair.html)
- [Merkle tree (Wikipedia)](https://en.wikipedia.org/wiki/Merkle_tree)
