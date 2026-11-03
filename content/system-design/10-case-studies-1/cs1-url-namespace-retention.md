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

The exercise assumes about 500 stored bytes per mapping before database overhead. At the illustrative rate, retaining ten years of mappings means hundreds of billions of records and hundreds of terabytes before overhead. Copies and recovery need a separate budget.

How long must the code be? Using **base62**, each character is one of 62 symbols (`a–z`, `A–Z`, `0–9`). Every extra character multiplies the number of possible codes by 62:

```formula reference
C = 62^L
where
C: number of distinct codes of exactly the chosen length
L: code length in characters
62: alphabet size, using ten digits and 26 letters in each case
In words: each additional base62 character multiplies the available code space by 62; choose enough space for retained allocations, reserved codes and growth.
```

Compare capacity with the retained allocation forecast:

Six characters provide about 57 billion values; seven provide about 3.5 trillion. The latter covers the hypothetical ten-year need of 365 billion with space for growth and wasted ranges.

This headroom matters when allocating ranges, reserving aliases and planning growth.

The code-space limit and storage footprint are different constraints. A code length that fits the identifiers says nothing about whether the chosen store meets its query and recovery targets.

## Key takeaways

- Each additional base62 character multiplies the namespace by 62.
- Size the namespace against retained link count and spare capacity.
- Retained bytes, replicas and recovery costs need their own budget.

## Further reading

- [Python: numeric operations and divmod](https://docs.python.org/3/library/functions.html#divmod)
- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
