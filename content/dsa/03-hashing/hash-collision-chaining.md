---
id: hash-collision-chaining
title: Separate chaining and load
level: intermediate
minutes: 4
sourceLesson: hash-collisions
summary: A collision is expected once enough keys are stored.
---

A collision is expected once enough keys are stored. Chaining treats it as an ordinary case: the bucket contains a collection and equality identifies the requested key inside that collection.

However good the hash function, two keys will eventually want the same bucket. For independent uniform bucket choices, with 23 keys in 365 buckets the chance of at least one collision is already over 50% (the **birthday paradox**: 23 people in a room probably include two who share a birthday). So the real design question for a hash table is not *whether* collisions happen but *what to do* when they do.

There are two families of answer. **Separate chaining** lets a bucket hold many keys. **Open addressing** keeps one key per slot and, on a collision, looks for another slot in the same array.



## Separate chaining

Each bucket holds a small collection, usually a linked list, of every key that hashed there.

```
idx  bucket
 0   -> [k7]
 1   (empty)
 2   -> [k2] -> [k9] -> [k4]
 3   -> [k5]
```

- **Insert**: hash, then add to that bucket's list (after checking the key is not already there).
- **Look up**: hash, then scan that one list.
- **Delete**: unlink the node. Nothing else in the table is affected.

How long is a chain? Assume **simple uniform hashing** (every key is equally likely to land in any bucket, independently of the others) and that the key you look up is chosen at random. Then the average chain length equals the load factor, and the expected cost of a lookup is:

```formula
α = n / m
S_miss ≈ 1 + α
S_hit = 2 + (n − 1) / (2m)
α = 12 / 16 = 0.75
S_miss ≈ 1 + 0.75 = 1.75
S_hit = 2 + 11 / 32 ≈ 2.344
where
α: alpha, the load factor: average keys per bucket, here 0.75
n: the number of keys stored, here 12
m: the number of buckets, here 16
S_miss: the expected steps for an unsuccessful lookup (key absent): find the bucket, then scan its whole chain
S_hit: expected unit steps for a uniformly selected stored key: one hash/bucket step, its matching comparison, and half the expected other colliders
≈: approximately equal to
In words: a miss scans an average of three-quarters of a key after reaching the bucket. A hit must also compare with its own key; twelve uniformly placed keys in sixteen buckets give about 2.344 steps, rather than fewer than two.
```

The "1" is the cost of computing the hash and reaching the bucket. These are averages: an unlucky or attacked table can still put many keys in one chain.

Chaining is simple and degrades gracefully: α can go above 1 (more keys than buckets) and the table still works, just more slowly. Its costs are memory and locality. In a node-based linked-list implementation, each entry has a `next` pointer and may live in a separate allocation. Following those pointers can incur cache misses; their importance depends on representation and workload.

Java's `HashMap`, common C++ `std::unordered_map` implementations and many textbook tables use chaining. The C++ standard specifies bucket and reference-stability requirements, without mandating one physical layout.

## Capacity versus collision strategy

Linear probing, double hashing and Robin Hood hashing are all open-addressing designs: one slot holds at most one key. Rearranging keys or changing the next candidate slot does not create extra storage. Separate chaining can store more keys than buckets because each bucket owns a collection rather than a single-key slot. Later units examine how the open-addressing sequences work, but this capacity distinction already follows from where entries live.

## Key takeaways
- Each bucket holds a collection, so the load factor can exceed one.
- Expected chain costs assume uniform hashing and a randomly selected successful key.
- Per-node pointers and cache misses are important practical costs.

## Further reading
- [Open addressing — Wikipedia](https://en.wikipedia.org/wiki/Open_addressing)
