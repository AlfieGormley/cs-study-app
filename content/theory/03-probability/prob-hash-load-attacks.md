---
id: prob-hash-load-attacks
title: Analyse hashing load and adversarial keys
level: advanced
minutes: 4
sourceLesson: prob-algorithms
summary: Expected bucket occupancy is the load factor under uniform hashing.
---

## Hash tables and collisions

Hash keys into buckets, each key independently to a uniformly random bucket (the **simple uniform hashing** assumption). By indicators and linearity, the expected number of keys in each bucket is the **load factor**, and the expected number of pairs of keys that land in the same bucket follows from counting pairs:

```formula
α = n / m
E[K_b] = n × (1/m) = α
E[N_c] = C(n, 2) × (1/m)
E[N_c] = (n(n − 1)) / (2m)
where
n: the number of keys stored
m: the positive integer number of buckets
α: alpha, the load factor, the average number of keys per bucket
K_b: the number of keys in one particular bucket b
1/m: the chance a key lands in a given bucket, and the chance two keys land in the same bucket
N_c: the number of colliding pairs, pairs of keys in the same bucket
C(n, 2): "n choose 2", the number of pairs of keys, n × (n − 1) / 2
E[ ]: expected value
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: each bucket gets α keys on average, and with n keys there are about n²/2 pairs, each colliding with chance 1/m.
```

An unsuccessful search in a **chained table** (each bucket holds a list of its keys) inspects about α keys on average, plus the cost of hashing, so lookups are O(1 + α), where O( ) is big-O notation, "grows at most as fast as".

The colliding-pairs result is surprising. With as many keys as buckets, the load factor is one and you expect about half as many colliding pairs as keys: 1,000 keys in 1,000 buckets give 1000 × 999 / 2000 ≈ 500. Collisions are not a rare failure; they are the normal state of a hash table, which is why every hash table needs a collision strategy.

> [!note] Real tables resize
> CPython's dictionary implementation uses a usable-entry fraction of about two-thirds; deletions and table layout complicate a simple occupancy trigger. Java `HashMap` has a configurable load factor, default 0.75. These are implementation/default details, not universal rules for all hash tables. Keeping the load factor bounded keeps the expected cost constant. **Open addressing** (storing every key in the array itself and probing other slots on a collision) degrades sharply as the load factor approaches 1.

In the classical large-table model with uniform independent home positions and no deletions, **linear probing** (trying the next slot, then the next) has this expected cost for an unsuccessful search:

```formula
U ≈ 1/2 × (1 + 1 / (1 − α)^2)
U ≈ 1/2 × (1 + 1 / 0.1^2) = 50.5
where
U: the expected number of probes (slots examined) in an unsuccessful search
α: alpha, the occupied fraction, at least 0 and strictly below 1; 0.9 in the second line
(1 − α)^2: the free fraction of slots, squared
≈: approximately equal to (valid for large tables)
In words: at 90% full, a failed lookup examines about 50 slots, versus 2.5 at 50% full.
```

## Adversaries and hash flooding

The uniform-hashing assumption fails if an attacker chooses the keys. In 2011, researchers showed that web frameworks in PHP, Java, Python and others could be knocked over by POST requests whose parameter names all hashed to one bucket, making each insert cost O(n) work, where n is the number of keys already in that bucket. Defences include capping the number of request parameters and secret keyed hashing. Python enables hash randomisation for str and bytes by default since 3.3; CPython commonly uses SipHash, with the active algorithm visible in `sys.hash_info`. Configuration can disable randomisation, and custom or non-string hashes need separate consideration. A random seed alone is not a guarantee against every adaptive attack.

## Key takeaways
- Expected bucket occupancy is the load factor under uniform hashing.
- Untrusted keys can defeat an unkeyed uniform model.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
