---
id: hash-resize-java-bins
title: Java HashMap: splitting and tree bins
level: intermediate
minutes: 5
sourceLesson: hash-resizing
summary: This unit follows OpenJDK 21 ordinary put and resize paths.
---

This unit follows OpenJDK 21 ordinary put and resize paths. Distinguish normal load-triggered growth from a collision-triggered request to resize or treeify a bucket.

## How Java's HashMap works

Java's `HashMap` uses separate chaining over an array whose length is always a power of two (default 16).

**Spreading the hash.** In Java's source the bucket index is `(n − 1) & hash`, where `n` is the table length (not the number of keys) and `&` is bitwise AND. Because the length is a power of two, this is the same as the remainder:

```formula
b = H mod m
b = 53 mod 16 = 5
where
b: the bucket index, from 0 to m − 1
H: the (spread) hash value of the key, here 53
m: the table length, a power of two; here 16
mod: "modulo", the remainder after division; for a power-of-two m it equals the low bits of H (53 is 110101 in binary, and its low four bits, 0101, are 5)
In words: Java keeps only the low bits of the hash, so a hash of 53 in a 16-bucket table goes to bucket 5.
```

Using only the low bits is fast, but it ignores the high bits. To stop poor `hashCode()` implementations that differ only in their high bits from colliding, Java first mixes the high half into the low half:

```java
static int hash(Object key) {
  int h;
  // Fold high bits into low bucket bits.
  return key == null ? 0
    : (h = key.hashCode()) ^ (h >>> 16);
}
```

**Resizing.** Java resizes when the number of entries goes *above* a threshold:

```formula
T = C L
T = 16 × 0.75 = 12
where
T: the threshold, the largest number of entries the table may hold before it doubles
C: the capacity, the number of buckets; here the default 16
L: the maximum load factor; here the default 0.75
In words: the threshold is buckets times the maximum load factor; a default map holds 12 entries and doubles when the 13th is added.
```

It doubles. Because the size is a power of two, each entry in old bucket i goes either to bucket i or to bucket i + oldCapacity in the new table, depending on one bit of its hash (`hash & oldCap`). Java 8 uses this to split each chain into "low" and "high" lists in a single pass, preserving order.

**Tree bins (Java 8).** JEP 180 added protection against long chains. In OpenJDK 21, ordinary `put` invokes treeification when adding a ninth node to a chain of eight (`TREEIFY_THRESHOLD` is 8). Other insertion paths can reach the threshold differently. A tree bin gives logarithmic lookup when hashes or a consistent comparable-key order distinguish keys. Two conditions apply:

- If the whole table has fewer than **64** buckets (`MIN_TREEIFY_CAPACITY`), Java resizes the table instead, since a small table is the likelier cause of the long chain.
- When a resize splits a tree bin and a part has **6** or fewer entries (`UNTREEIFY_THRESHOLD`), it turns back into a list. The gap between 8 and 6 avoids flipping back and forth.

Tree nodes are ordered by hash, then by `compareTo` if the keys are `Comparable`. For keys with identical hashes that are not comparable, the tree cannot order them meaningfully, so the guarantee is weaker; `String` keys, the usual flooding target, are comparable.

> [!example] How rare are tree bins?
> The HashMap source notes that with random hash codes and a default maximum load factor of 0.75, bucket sizes follow a **Poisson distribution** with mean about 0.5. Under that approximate model, the probability of exactly 8 entries is about 0.00000006 (worked out below); this is not a measured treeification rate. Tree bins are a defence against bad or malicious hashes, not a normal-case optimisation.

The Poisson distribution gives the chance of seeing exactly k events when they happen independently at an average rate λ. Here an "event" is a key landing in a particular bucket:

```formula
P(k) = e^(−λ) × λ^k / k!
P(8) = e^(−0.5) × 0.5^8 / 8!
P(8) = 0.6065 × 0.00390625 / 40320
P(8) ≈ 0.00000006
where
P(k): the probability that a given bucket holds exactly k entries
k: the number of entries in the bucket, here 8
λ: lambda, the average number of entries per bucket, here about 0.5
e: Euler's number, about 2.718; e^(−0.5) ≈ 0.6065
!: factorial, the product of all whole numbers up to that one; 8! = 8 × 7 × … × 1 = 40,320
^: "to the power of"
≈: approximately equal to
In words: with an average of half an entry per bucket, a bucket reaching 8 entries by chance happens about 6 times in 100 million buckets.
```

## Key takeaways
- Hash spreading folds high bits into low bucket bits.
- Doubling separates old chains by one additional hash bit.
- Tree-bin bounds need distinguishable hashes or comparable ordering; small tables resize first.

## Further reading
- [HashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
- [JEP 180: Handle Frequent HashMap Collisions with Balanced Trees](https://openjdk.org/jeps/180)
- [OpenJDK 21 HashMap source](https://raw.githubusercontent.com/openjdk/jdk21u/master/src/java.base/share/classes/java/util/HashMap.java)
