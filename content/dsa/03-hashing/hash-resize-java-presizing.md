---
id: hash-resize-java-presizing
title: Java HashMap capacity planning
level: intermediate
minutes: 3
sourceLesson: hash-resizing
summary: A constructor’s capacity argument is not the number of entries you can hold at the default load factor.
---

A constructor’s capacity argument is not the number of entries you can hold at the default load factor. Plan for the threshold after power-of-two rounding, and remember the backing array is allocated lazily.

## Pre-sizing a Java HashMap

 `new HashMap<>(1000)` rounds the capacity up to 1,024, whose threshold is 768, so it still resizes once before reaching 1,000 entries. To hold a given number of entries without resizing, the threshold must be at least that number:

```formula
C ≥ n / L
C ≥ 1000 / 0.75
1000 / 0.75 ≈ 1333.3
where
C: the capacity (buckets) to request, which Java rounds up to a power of two
n: the number of entries you plan to store, here 1,000
L: the maximum load factor, here the default 0.75
≈: approximately equal, rounding the fractional capacity requirement
≥: "is at least"
In words: ask for at least the planned entry count divided by 0.75; 1,000 entries need a capacity of 1,334 or more, which Java rounds up to 2,048 buckets (threshold 1,536).
```

Java 19 added `HashMap.newHashMap(n)`, which does that calculation for you.

## Trace the capacity changes

With the default threshold policy and well-distributed keys, a map that begins at sixteen buckets first allocates its backing array on insertion. Initial allocation is not a doubling. Its entry limits before successive doublings are twelve, twenty-four, forty-eight, ninety-six, one hundred and ninety-two, three hundred and eighty-four, then seven hundred and sixty-eight. Inserting a thousand distinct keys crosses all seven limits, leaving a capacity of two thousand and forty-eight buckets.

Now compare a constructor argument of one thousand. Java rounds that capacity request to one thousand and twenty-four buckets, but the default threshold is only seven hundred and sixty-eight entries. It therefore still needs one doubling before storing a thousand entries. A capacity request of one thousand three hundred and thirty-four rounds to two thousand and forty-eight buckets and leaves room for one thousand five hundred and thirty-six entries at the default load factor.

A larger load factor changes the threshold, so capacity planning cannot ignore the constructor’s second argument. It trades fewer empty buckets against longer collision chains. Nor does pre-sizing prove that every put takes constant time: constructing keys, hashing, equality, allocation and adversarial collisions remain separate costs. Collision-triggered requests to resize can also affect a small table even before its ordinary size threshold is crossed.

Use the Java 19 convenience factory when the input is an expected entry count. Use an explicit capacity when you deliberately need to control the bucket and load policy. In either case, estimate the peak live count rather than a daily cumulative count if entries are continually removed.

## Key takeaways
- Capacity arguments and expected entry counts are different.
- Include the load factor and power-of-two rounding when planning capacity.
- Pre-sizing avoids planned load-triggered doublings, without guaranteeing every operation’s latency.

## Further reading
- [HashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
- [JEP 180: Handle Frequent HashMap Collisions with Balanced Trees](https://openjdk.org/jeps/180)
- [OpenJDK 21 HashMap source](https://raw.githubusercontent.com/openjdk/jdk21u/master/src/java.base/share/classes/java/util/HashMap.java)
