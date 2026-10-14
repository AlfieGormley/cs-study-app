---
id: hash-function-bucket-bits
title: Hash quality and bucket reduction
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: A full hash and a bucket index are different things.
---

A full hash and a bucket index are different things. Even a valid hash can perform badly if reducing it to a slot preserves patterns in the input.

A hash table is only as good as its hash function. Feed it keys that the function spreads evenly and every bucket holds about one key. Feed it keys that the function clumps together and the table turns into a slow list.

This lesson covers what "good" means, the classic ways to build a hash, and how languages responded differently to hash-flooding attacks after 2011.



## What a table hash needs

A hash function maps a key of any size to a fixed-size integer. For a hash table it must be:

1. **Deterministic.** The same key always gives the same hash, at least within one run of the program.
2. **Consistent with equality.** If `a == b`, then `hash(a) == hash(b)`.
3. **Uniform.** Keys spread evenly over the output range, *including* the patterned keys real programs produce: sequential IDs, multiples of 1,000, strings sharing a long prefix.
4. **Fast.** It runs on every lookup, so a few nanoseconds matters.

A good hash also has the **avalanche** property: flipping one input bit flips about half the output bits. That stops similar keys (`user1`, `user2`) landing in nearby slots.

Table hashes are not cryptographic hashes. SHA-256 is designed to make finding two inputs with the same output computationally infeasible, and pays for that in speed. A table only needs a good spread, so it uses fast non-cryptographic functions such as MurmurHash, xxHash or wyhash, or a keyed function such as SipHash when attackers control the keys (see below).



## From hash to bucket: the division method

The simplest way to turn an integer key into one of m buckets is to divide by m and keep the remainder:

```formula
h(k) = k mod m
h(40) = 40 mod 13 = 1
where
h(k): the bucket index the hash gives key k, a whole number from 0 to m − 1
k: the integer key being stored, here 40
m: the number of buckets in the table, here 13
mod: "modulo", the remainder after whole-number division; 40 mod 13 = 1 because 40 = 3 × 13 + 1
In words: divide the key by the number of buckets and use the remainder as the bucket number; key 40 in a 13-bucket table goes to bucket 1.
```

It is fast, but the choice of m matters enormously. Take keys that are all multiples of 8 (common for memory addresses and aligned sizes):

```
keys:      8  16  24  32  40  48  56  64
mod 16:    8   0   8   0   8   0   8   0
mod 13:    8   3  11   6   1   9   4  12
```

With sixteen buckets, the keys use only 2 of 16 buckets. With thirteen buckets, they spread over 8 different buckets. When m is a power of two (2, 4, 8, 16, …), reducing the integer key modulo the bucket count just keeps the key’s low bits: 40 is 101000 in binary, and the remainder after division by sixteen is eight, its last four bits, 1000. So any pattern in the low bits goes straight into the bucket index. The textbook advice is to choose m as a **prime not close to a power of two**.

## Key takeaways
- Hashing must respect equality and remain deterministic for the table’s lifetime.
- Power-of-two remainder selection exposes patterns in low bits.
- A cryptographic collision guarantee is different from useful bucket distribution.

## Further reading
- [Hash function — Wikipedia](https://en.wikipedia.org/wiki/Hash_function)
