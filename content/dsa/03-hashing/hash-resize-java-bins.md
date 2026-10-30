---
id: hash-resize-java-bins
title: Java HashMap: splitting and tree bins
level: intermediate
minutes: 5
sourceLesson: hash-resizing
summary: Java's HashMap folds high hash bits into the index, splits each chain in one pass when doubling, and turns very long chains into trees.
---

Java's `HashMap` is a chaining table with three refinements worth knowing: it mixes high hash bits into the bucket index, it splits chains cheaply when it doubles, and it turns very long chains into balanced trees. This lesson follows OpenJDK 21's ordinary `put` and resize paths.

## How Java's HashMap works

Java's `HashMap` uses separate chaining over an array whose length is always a power of two (default 16).

**Spreading the hash.** In Java's source the bucket index is `(n - 1) & hash`, where `n` is the table length (not the number of keys) and `&` is bitwise AND. Because the length is a power of two, this keeps the hash's low bits, the same as taking its remainder after dividing by the length: a hash of 53 (binary 110101) in a 16-bucket table goes to bucket 5 (binary 0101).

Using only the low bits is fast, but it ignores the high bits. To stop poor `hashCode()` implementations that differ only in their high bits from colliding, Java first mixes the high half into the low half:

```java
static int hash(Object key) {
  int h;
  // Fold high bits into low bucket bits.
  return key == null ? 0
    : (h = key.hashCode()) ^ (h >>> 16);
}
```

**Resizing.** Java resizes when the number of entries goes *above* a threshold: capacity times the maximum load factor. A default map has 16 buckets and a load factor of 0.75, so it holds 12 entries and doubles when the 13th is added.

Because the size is a power of two, doubling sends each entry in old bucket i either to bucket i or to bucket i + oldCapacity in the new table, depending on one bit of its hash (`hash & oldCap`). Java 8 uses this to split each chain into "low" and "high" lists in a single pass, preserving order.

**Tree bins (Java 8).** JEP 180 added protection against long chains. In OpenJDK 21, ordinary `put` invokes treeification when adding a ninth node to a chain of eight (`TREEIFY_THRESHOLD` is 8). Other insertion paths can reach the threshold differently. A tree bin gives logarithmic lookup when hashes or a consistent comparable-key order distinguish keys. Two conditions apply:

- If the whole table has fewer than **64** buckets (`MIN_TREEIFY_CAPACITY`), Java resizes the table instead, since a small table is the likelier cause of the long chain.
- When a resize splits a tree bin and a part has **6** or fewer entries (`UNTREEIFY_THRESHOLD`), it turns back into a list. The gap between 8 and 6 avoids flipping back and forth.

Tree nodes are ordered by hash, then by `compareTo` if the keys are `Comparable`. For keys with identical hashes that are not comparable, the tree cannot order them meaningfully, so the guarantee is weaker; `String` keys, the usual flooding target, are comparable.

> [!example] How rare are tree bins?
> The HashMap source notes that with random hash codes and a default maximum load factor of 0.75, bucket sizes follow a **Poisson distribution** with mean about 0.5. Under that approximate model, the probability of exactly 8 entries is about 0.00000006 (see the reference maths below); this is not a measured treeification rate. Tree bins are a defence against bad or malicious hashes, not a normal-case optimisation.

The Poisson distribution gives the chance of seeing exactly k events when they happen independently at an average rate λ. Here an "event" is a key landing in a particular bucket:

```formula reference
P(k) = e^(−λ) λ^k / k!
where
P(k): the probability that a given bucket holds exactly k entries
k: the number of entries in the bucket
λ: lambda, the average number of entries per bucket, about 0.5 in the HashMap source's model
e: Euler's number, about 2.718
!: factorial, the product of all whole numbers from 1 up to that one; 8! = 40,320
^: "to the power of"
In words: with an average of half an entry per bucket, the chance of a bucket reaching 8 entries by luck is about 6 in 100 million, so a tree bin almost always signals a bad or hostile hash.
```

## Key takeaways
- Hash spreading folds high bits into low bucket bits.
- Doubling separates old chains by one additional hash bit.
- Tree-bin bounds need distinguishable hashes or comparable ordering; small tables resize first.

## Further reading
- [HashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
- [JEP 180: Handle Frequent HashMap Collisions with Balanced Trees](https://openjdk.org/jeps/180)
- [OpenJDK 21 HashMap source](https://raw.githubusercontent.com/openjdk/jdk21u/master/src/java.base/share/classes/java/util/HashMap.java)
