---
id: hash-collision-swiss-designs
title: Swiss tables and collision trade-offs
level: intermediate
minutes: 3
sourceLesson: hash-collisions
summary: Metadata can make a table search cheap before it touches a key or value.
---

Metadata can make a table search cheap before it touches a key or value. Swiss tables use short hash fingerprints to reject most slots in a group; a fingerprint match still requires checking the real key.

## Modern designs: Swiss tables

Google's **Swiss tables** (Abseil `flat_hash_map`, presented in 2017) are open addressing with a twist. Alongside the slots is an array of one-byte **control bytes**, each holding "empty", "deleted" or 7 bits of the key's hash. On Abseil's x86 SSE2 path, a lookup loads 16 control bytes and uses SIMD instructions to compare all 16 against the key's 7 bits in a single step, only touching the slots that match. Tables run at up to 7/8 full while lookups stay fast.

Rust (via the `hashbrown` crate) and, since Go 1.24, Go's built-in map use Swiss-table designs; Go uses eight-slot groups, so Swiss-table designs do not all probe 16 slots.

Another option is **cuckoo hashing**, where each key has two possible slots and inserts evict residents to their alternative slot. The classic two-hash, single-slot, no-stash version checks at most two candidate slots; insertion can trigger rehashing. Bucketed or stashed variants have different lookup bounds.



## Choosing between them

| | Chaining | Open addressing |
|---|---|---|
| Load factor | can exceed 1 | at most 1; normally kept below it |
| Memory | node + pointer each | one flat array |
| Cache behaviour | pointer chasing | contiguous |
| Delete | trivial | tombstones or shifting |
| Near full | slows gently | slows sharply |

Chaining is the safer general-purpose choice when keys are large or the load is unpredictable, and it lets you swap the chain for a tree (Java HashMap: splitting and tree bins). Open addressing can offer good locality and low overhead at controlled load; actual speed depends on key size, hash cost and workload.

## Fingerprints are candidates, not equality

A seven-bit fingerprint has only 128 possible values. Several distinct keys can therefore match the same control byte. The vector comparison creates a shortlist; the table still checks the actual key for every surviving candidate. The control-byte shortcut reduces unnecessary memory accesses without changing the equality contract.

Deletion markers and empty markers also remain distinct metadata states. A lookup can use an empty marker to establish a stopping condition according to the table’s probing rules; a deleted slot may require continuing to another group. Group width is a property of the implementation and hardware path, so copying a statement about Abseil’s sixteen-byte comparison to every Swiss-table implementation would be wrong.

When comparing designs, measure the workload you actually have. Small inline keys and values benefit from a flat layout differently from large objects reached through pointers. The hash computation itself can dominate when keys are long, and references into a flat container may have different stability guarantees from references into a node-based container. Choose the API contract as well as a favourable average probe count.

## Key takeaways
- Swiss-table metadata rejects most candidate slots before touching full keys.
- Fingerprint matches still need equality checks.
- Group widths and reference stability depend on the implementation.

## Further reading
- [Swiss tables design notes — Abseil](https://abseil.io/about/design/swisstables)
- [Cuckoo hashing — Wikipedia](https://en.wikipedia.org/wiki/Cuckoo_hashing)
- [Go Swiss-table implementation](https://go.dev/blog/swisstable)
