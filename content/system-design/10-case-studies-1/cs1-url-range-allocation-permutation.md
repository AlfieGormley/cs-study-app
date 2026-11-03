---
id: cs1-url-range-allocation-permutation
title: Allocate counter ranges and permute codes
level: intermediate
minutes: 4
summary: Allocate non-overlapping ranges durably and never reuse them after crashes.
sourceLesson: cs1-url-shortener
---

The previous unit compared truncated hashes and Snowflake IDs. This unit develops the counter alternative: keep codes short and collision-free while moving coordination out of the per-link hot path.

### Option B: A counter, base62-encoded

Give each link the next integer and base62-encode it. Base62 is ordinary place-value notation, like decimal, but each position is worth 62 times the one to its right instead of 10 times. For example, with digits ordered `0–9`, `a–z`, `A–Z`, the counter value 125 encodes as `21`: two groups of 62 and one remainder.

Each additional position is worth 62 times the preceding position.

- **Pro**: unique allocations when counters and ranges never overlap or wrap, with a compact encoding.
- **Con**: a single global counter is a bottleneck and single point of failure.
- **Fix: range allocation.** A coordination service (a small database table, ZooKeeper or etcd) hands each write server a *block* of, say, 1 million IDs. The server allocates from its block in memory and only goes back for a new block when it runs out. Servers contact the coordinator only to reserve another range, rather than for every link. If a server crashes, the rest of its block is simply wasted. Include abandoned ranges in the namespace budget rather than reusing uncertain IDs.
- **Con: guessable.** Sequential codes make neighbouring allocations easy to enumerate. A reversible permutation can disguise the sequence while preserving unique values, but a simple multiply-and-wrap mapping is only obfuscation: observations can reveal its pattern. Use authentication or sufficiently strong random capability tokens when access must be restricted. A short code or custom permutation is not established as secure here.

Larger ranges reduce how often servers contact the coordinator, but increase the possible waste after a crash. Startup allocations can arrive together, so a steady-state average is not a bound on coordination bursts.

The multiply-and-wrap bijective permutation from the "guessable" bullet looks like this:

```formula reference
m = (an) mod C
where
n: allocated counter value, a whole number from zero up to but excluding C
C: number of values in the code space
a: integer multiplier coprime with C, meaning their only shared positive factor is one
m: permuted value to encode as a short code
mod: remainder after division, keeping the output inside the same code space
In words: multiplying by a value coprime with the space size and wrapping by the remainder gives a one-to-one rearrangement; this preserves uniqueness but does not provide secrecy.
```

### Option D: Pre-generated key service

A key generation service pre-computes random 7-character codes, atomically rejects duplicate candidates, stores distinct values in an "unused" table, and durably assigns disjoint batches to write servers. It's essentially Option B with random rather than sequential codes. It works, but you have to store and manage billions of unused keys.

> [!tip] Recommended answer
> Range-allocated counters with a bijective permutation, base62-encoded to 7 characters. Collision-free and short when ranges are never reused; the bijective permutation is not an access-control mechanism, and the coordinator is touched only once per million links.

> [!analogy] Real-world analogy: Books of numbered tickets
> Each desk receives a different book of numbered tickets. If a partly used book is lost, its remaining numbers are retired.
>
> **How it maps:** A reserved ID range lets each server allocate locally; retiring uncertain numbers prevents another server from issuing them again.
>
> **Where it stops:** The coordinator must durably enforce non-overlap, and changing how ticket numbers look does not control who can use a link.

## Key takeaways

- Allocate non-overlapping ranges durably and never reuse them after crashes.
- A coprime multiply-and-wrap mapping preserves uniqueness.
- A bijection is not authorisation or proof of cryptographic security.

## Further reading

- [Python: numeric operations and divmod](https://docs.python.org/3/library/functions.html#divmod)
- [DynamoDB: conditional writes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html)
