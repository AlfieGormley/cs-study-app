---
id: prob-hash-load-attacks
title: Analyse hashing load and adversarial keys
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: Expected bucket occupancy is the load factor under uniform hashing.
---

A hash table's expected performance depends on how keys reach buckets. **Simple uniform hashing** assumes each key independently chooses a uniformly random bucket. Real implementations and adversarial inputs need separate scrutiny.

## Average occupancy is not the worst bucket

The **load factor** is stored keys divided by buckets. Under the uniform model, it is the expected occupancy of a specified bucket. In a **chained hash table**, an unsuccessful lookup scans its selected bucket; with bounded-cost hashing and comparisons, keeping the load factor bounded keeps expected lookup cost bounded.

Collisions are ordinary. More keys create more pairs that can collide, even when each bucket's expected occupancy looks small. The mean occupancy does not guarantee short chains in every bucket.

**Open addressing** stores keys directly in slots and probes alternatives after a collision. As the table fills, searches for an empty slot become harder. Linear probing can form long runs of occupied slots, so a high load factor hurts more than a simple occupancy average suggests.

## Challenge the input model

An attacker able to construct colliding keys can defeat uniform-model expectations. In a list-backed bucket, each insertion may scan existing keys; a large batch then causes quadratic total work, where input size means the number of supplied keys.

Resizing may separate keys that only shared a bucket index, but it cannot separate identical full hash values under the same hash function. An appropriate secret keyed hash makes precomputed attacks harder. Input limits still matter, as do key types, key handling and adaptive attackers.

Python randomises hashes for covered string and byte keys by default; configuration and other key types need checking. Do not infer that every object is protected merely because a process has a hash seed.

## Key takeaways
- Uniform expected occupancy is not a maximum-load guarantee.
- High occupancy particularly hurts probing schemes.
- Untrusted keys require defences beyond an average-case model.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
