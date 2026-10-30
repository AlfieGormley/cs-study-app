---
id: hash-resize-java-presizing
title: Java HashMap capacity planning
level: intermediate
minutes: 3
sourceLesson: hash-resizing
summary: A HashMap's capacity argument is not its entry limit; size for count divided by load factor, or use HashMap.newHashMap.
---

A `HashMap` constructor's capacity argument is not the number of entries the map can hold. Plan for the threshold after power-of-two rounding, or let Java do the calculation for you.

## Pre-sizing a Java HashMap

`new HashMap<>(1000)` rounds the capacity up to the next power of two, 1,024, but at the default load factor of 0.75 its threshold is only 768 entries. It therefore still doubles once before reaching 1,000 entries. To hold a planned number of entries without any doubling, the threshold must be at least that number, so the capacity must be at least the entry count divided by the load factor:

```formula reference
C ≥ n / L
where
C: the capacity (buckets) to request, which Java rounds up to a power of two
n: the number of entries you plan to store
L: the maximum load factor, 0.75 by default
≥: "is at least"
In words: ask for at least the planned entry count divided by the load factor. For 1,000 entries at 0.75 that means a capacity of 1,334 or more, which Java rounds up to 2,048 buckets with a threshold of 1,536.
```

Java 19 added `HashMap.newHashMap(n)`, which does that calculation for you: `HashMap.newHashMap(1000)` gives 2,048 buckets.

## What happens without pre-sizing

A default map starts at 16 buckets, allocating its array lazily on the first insert; that first allocation is not a doubling. Its thresholds then run 12, 24, 48, 96, 192, 384, 768. Loading 1,000 distinct keys crosses all seven, so the map doubles seven times, rehashing everything present each time, and ends with 2,048 buckets. That is the same final size a pre-sized map starts with, reached through seven pauses.

A larger load factor raises the threshold, so capacity planning must include the constructor's second argument: `new HashMap<>(1000, 1.0f)` holds 1,000 entries in 1,024 buckets without doubling, at the price of slightly longer chains.

Pre-sizing does not make every `put` constant-time: building keys, hashing, equality, allocation and adversarial collisions remain separate costs, and collision-triggered resizes can still affect a small table before its ordinary size threshold. Use the factory when you know the expected entry count, and an explicit capacity when you deliberately need to control the bucket count and load policy. If entries are continually removed, plan for the peak number alive at once, not a cumulative daily count.

## Key takeaways
- Capacity arguments and expected entry counts are different.
- Include the load factor and power-of-two rounding when planning capacity.
- Pre-sizing avoids planned load-triggered doublings, without guaranteeing every operation’s latency.

## Further reading
- [HashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
- [JEP 180: Handle Frequent HashMap Collisions with Balanced Trees](https://openjdk.org/jeps/180)
- [OpenJDK 21 HashMap source](https://raw.githubusercontent.com/openjdk/jdk21u/master/src/java.base/share/classes/java/util/HashMap.java)
