---
id: cs2-web-crawler-seen-content
title: Crawler seen-URL memory
level: intermediate
minutes: 3
summary: Size exact URL state and Bloom filters without silently assuming perfect membership.
sourceLesson: cs2-web-crawler
---

Bandwidth is modest. The hard numbers are about **URLs**. Each page has dozens of outlinks, so the set of *discovered* URLs grows far faster than the set of fetched pages. Plan for about 10 B known URLs. An exact seen-URL set stores every URL, at roughly 100 bytes each:

```formula
X = U × L
X = 10,000,000,000 × 100 B
X = 10^12 B ≈ 1 TB
where
X: size of an exact seen-URL set
U: URLs known to the crawler; here 10 billion
L: average stored size of one URL, in bytes (B); about 100
B: bytes
TB: terabytes, 10^12 bytes
≈: approximately equal to
In words: storing 10 billion URLs exactly takes about a terabyte, which needs disk or a key-value store.
```

A **Bloom filter** stores only a few bits per URL, at the price of occasional false positives. The standard sizing formula for a Bloom filter with the best number of hash functions is:

```formula
b = −ln(p) / (ln(2))^2
b = −ln(0.01) / (0.693147)^2
b = 4.605170 / 0.480453 ≈ 9.6 bits/URL
where
b: bits of filter memory needed per stored URL
p: the target false-positive rate, as a fraction; 1% = 0.01
ln: the natural logarithm, the logarithm to base e (e is about 2.718)
−: minus; ln of a number below 1 is negative, so the minus sign makes b positive
^2: squared (multiplied by itself)
bits: binary digits (0 or 1)
URL: one web address
≈: approximately equal to
In words: a 1% false-positive rate costs about 9.6 bits for every URL stored, however long the URL is.
```

Multiply by the number of URLs, divide by 8 for bytes, and pick the number of hash functions:

```formula
M = b × U / 8
M = 9.6 × 10,000,000,000 / 8 ≈ 12 GB
k = b × ln(2) = 9.6 × 0.693 ≈ 7
where
M: total Bloom filter size, in bytes
b: bits per URL; about 9.6 for 1%
U: URLs stored; here 10 billion
8: bits per byte
k: the best number of hash functions; each URL sets and checks k bits
ln: natural logarithm; ln(2) ≈ 0.693
GB: gigabytes, 1,000,000,000 bytes
≈: approximately equal to
In words: 10 billion URLs at 9.6 bits each is about 12 gigabytes, using 7 hash functions.
```

These formulas assume the hash functions behave like independent random choices and that you know the item count in advance; a filter filled beyond its planned size has a higher false-positive rate.

A 12 GB Bloom filter fits in RAM, split across a few nodes. An exact 1TB set usually motivates disk-backed or distributed storage; it is not inherently impossible to keep it in a large RAM cluster. This trade-off returns in the dedup section.


## Key takeaways
- Budget discovered URLs separately from fetched page bodies.
- Independent-hash Bloom sizing trades bits per item against false positives.
- Rediscovery does not repair a stable Bloom false positive.

## Further reading
- [Bloom filters](https://en.wikipedia.org/wiki/Bloom_filter)
