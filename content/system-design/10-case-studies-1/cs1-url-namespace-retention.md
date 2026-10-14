---
id: cs1-url-namespace-retention
title: Choose code length from namespace and retention
level: intermediate
minutes: 3
summary: Each additional base62 character multiplies the namespace by 62.
sourceLesson: cs1-url-shortener
---

The scenario creates 100 million links a day and keeps ten years of mappings. Traffic and cache misses were sized in the preceding unit; now choose a code length that lasts for the retained dataset.

## Retention and code capacity

Storage, keeping links for 10 years at about 500 bytes each (long URL, code, owner, timestamps), is the number of links times the size of each:

```formula
links = 100M × 365 × 10 = 365 bn
size = 365 bn × 500 B = 182.5 TB
replicated = 182.5 TB × 3 = 547.5 TB
where
links: links stored after 10 years at 100 million a day for 365 days a year
size: raw bytes for those links
replicated: the footprint with three copies of everything (3x replication)
M: million (10^6)
bn: billion (10^9)
B: bytes; one byte is 8 bits
TB: terabyte, 10^12 bytes
≈: approximately equal to (rounded)
In words: the raw size is 182.5 TB and three copies total 547.5 TB; round those final estimates to about 180 TB and 550 TB.
```

How long must the code be? Using **base62**, each character is one of 62 symbols (`a–z`, `A–Z`, `0–9`). Every extra character multiplies the number of possible codes by 62:

```formula
codes = 62^L
62^6 ≈ 5.7 × 10^10
62^7 ≈ 3.5 × 10^12
62^8 ≈ 2.2 × 10^14
where
codes: how many different codes of exactly that length exist
62: the number of characters in the base62 alphabet (10 digits + 26 lower-case + 26 upper-case letters)
L: the code length in characters
62^L: L copies of 62 multiplied together
10^10, 10^12, 10^14: 1 followed by 10, 12 or 14 zeros: 57 billion, 3.5 trillion and 218 trillion codes
≈: approximately equal to (rounded)
In words: each extra character makes 62 times as many codes, so 7 characters give about 3.5 trillion.
```

To see how long a code space lasts, divide it by the links created per year:

```formula
years = codes / (daily × 365)
years = 57B / (100M × 365) ≈ 1.6
ratio = 3.5T / (365B) ≈ 9.6
where
years: how long until every code of that length is used
codes: the code space, here 57 billion for 6 characters
daily: new links per day, here 100 million
ratio: how many times the 7-character space (3.5 trillion) covers the 10-year need of 365 billion links
M: million (10^6)
B: billion (10^9)
T: trillion (10^12)
≈: approximately equal to (rounded)
In words: six characters run out in about a year and a half; seven give about ten times the ten-year need.
```

Six characters would run out in about 1.6 years. **Seven** gives 3.5 trillion, about ten times our 10-year need. That headroom matters for one of the ID strategies below.


What the numbers tell us: writes are modest, reads are high but cache well, and storage (180 TB raw, over half a petabyte replicated) motivates evaluating horizontal partitioning, storage tiers and recovery costs; raw size alone does not prove a universal single-node limit.

## Key takeaways

- Each additional base62 character multiplies the namespace by 62.
- Size the namespace against retained link count and spare capacity.
- Retained bytes, replicas and recovery costs need their own budget.

## Further reading

- [Python: numeric operations and divmod](https://docs.python.org/3/library/functions.html#divmod)
- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
