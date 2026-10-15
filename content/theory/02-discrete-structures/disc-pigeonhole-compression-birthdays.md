---
id: disc-pigeonhole-compression-birthdays
title: "Pigeonhole, compression and birthday collisions"
level: intermediate
minutes: 4
summary: "The fullest bin holds at least the average rounded up, regardless of the distribution."
sourceLesson: disc-counting
---

## The pigeonhole principle

**If there are more pigeons than holes, some hole has at least two pigeons.** More generally, if you spread items over boxes, some box must hold at least the average, rounded up:

```formula
L_max ≥ ⌈N / k⌉
⌈1,000,000 / 4,096⌉ = 245
where
L_max: the number of items in the fullest box
N: the number of items
k: the number of boxes, at least 1
⌈ ⌉: ceiling: round up to the nearest whole number, so ⌈244.14⌉ = 245 and ⌈3⌉ = 3
≥: is at least
In words: the boxes can't all be below average, and a box holds a whole number of items, so the fullest box holds at least the average rounded up.
```

The bound is the best possible: spreading the items as evenly as possible makes the fullest box equal to the average rounded up. It sounds trivial, but it proves things that are otherwise surprising:

- Among 13 people, two share a birth month.
- Hash 1,000,000 keys into 4,096 buckets and some bucket receives at least 245 keys (the example in the formula), however good the hash function.
- In a group of at least two people with mutual friendships and no self-friendships, two have the same number of friends within the group. In a group of 10, the possible friend counts are 0 to 9, but 0 and 9 can't both occur (someone with 9 friends is friends with everyone), so 10 people share at most 9 different counts.

### No compressor shrinks every file

A lossless compressor must be injective (different inputs give different outputs), or decompression would be ambiguous. Count the files of exactly n bits against all the strictly shorter ones:

```formula
2^0 + 2^1 + … + 2^{n−1} = 2^n − 1
where
n: the positive length of the input files, in bits; the zero-length input cannot be made strictly shorter either
2^n: the number of different files of exactly n bits (each bit is 0 or 1)
2^0, 2^1, …: the numbers of files of length 0, 1, … bits; the sum runs up to length n − 1
…: and so on, one term for each length
In words: there is exactly one fewer bit string shorter than n bits than there are strings of exactly n bits. For n = 3: 1 + 2 + 4 = 7 shorter strings, against 8 strings of 3 bits.
```

So no injective compressor can map all 2ⁿ inputs to shorter outputs. A compressor defined on all finite bit strings that shrinks some inputs must expand others (an identity encoding need not expand anything); format framing and block overhead are concrete reasons gzip or zstd output may grow. The counting argument proves that some growth is unavoidable for such a total shrinking compressor; it does not require a particular header design.

### The birthday problem

Pigeonhole is also the root of the **birthday problem**, which asks the harder question of when a collision becomes *likely* rather than *certain*. In the model of independent, uniformly distributed birthdays over 365 possible days, certainty needs 366 people, but 23 already give a better than 50% chance. For hashes, the same model gives:

```formula
N_coll ≈ 2^{b/2}
N_coll ≈ 2^32 ≈ 4.3 × 10^9   for b = 64
where
N_coll: the number of hashed items at which a collision (two items with the same hash) becomes reasonably likely
b: the number of bits in each hash output, so there are 2^b possible outputs
≈: roughly; collisions can also happen earlier
In words: with independent, uniformly distributed b-bit hash outputs, collisions become substantially likely around the square root of the number of possible outputs, not near the total. A 64-bit hash runs into them after a few billion items.
```

That probability calculation is covered in the probability module.

## Key takeaways

- The fullest bin holds at least the average rounded up, regardless of the distribution.
- Pigeonhole proves collisions inevitable; the birthday model estimates when random collisions become likely.

## Further reading

- [Pigeonhole principle — Wikipedia](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
