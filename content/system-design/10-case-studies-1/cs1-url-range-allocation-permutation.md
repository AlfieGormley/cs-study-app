---
id: cs1-url-range-allocation-permutation
title: Allocate counter ranges and shuffle codes
level: intermediate
minutes: 4
summary: Allocate non-overlapping ranges durably and never reuse them after crashes.
sourceLesson: cs1-url-shortener
---

The previous unit compared truncated hashes and Snowflake IDs. This unit develops the counter alternative: keep codes short and collision-free while moving coordination out of the per-link hot path.

### Option B: A counter, base62-encoded

Give each link the next integer and base62-encode it. Base62 is ordinary place-value notation, like decimal, but each position is worth 62 times the one to its right instead of 10 times. With the alphabet ordered `0–9`, `a–z`, `A–Z`:

```formula
n = 62d_1 + d_0
125 = 2 × 62 + 1 → "21"
62^7 − 1 → "ZZZZZZZ"
where
n: the counter value being encoded
d_0: the value of the rightmost character, from 0 to 61 (0–9 are 0–9, a–z are 10–35, A–Z are 36–61)
d_1: the value of the next character to the left, worth 62 each
62^7 − 1: the largest number that fits in 7 base62 characters, about 3.5 trillion
→: "is written as"
In words: 125 is two 62s plus one, so it is written "21"; the largest 7-character code, "ZZZZZZZ", stands for 62^7 − 1.
```

Longer codes just add positions worth 62², 62³ and so on.

- **Pro**: no collisions, ever. Codes are as short as possible.
- **Con**: a single global counter is a bottleneck and single point of failure.
- **Fix: range allocation.** A coordination service (a small database table, ZooKeeper or etcd) hands each write server a *block* of, say, 1 million IDs. The server allocates from its block in memory and only goes back for a new block when it runs out. At 3,000 writes/s, the coordinator is contacted once every few minutes (worked out below). If a server crashes, the rest of its block is simply wasted. With 3.5 trillion codes, wasting millions is irrelevant.
- **Con: guessable.** Sequential codes let anyone enumerate links (`aaaaaab`, `aaaaaac`...). Fix this by passing the counter through a reversible permutation before encoding: for example, multiply by a large constant that shares no factor with 62^7 (so not a multiple of 2 or 31) modulo 62^7, or use a small Feistel network keyed with a secret. It stays collision-free (it's a bijection) but looks random. The multiplication trick only hides the pattern from casual eyes (decoded codes from known consecutive counters reveal the multiplier through their modular difference); a vetted keyed permutation can hide sequence relationships, but a custom small Feistel construction is not established as secure here.

How often the coordinator is contacted is the block size divided by the write rate:

```formula
t = block / writes
t = 1,000,000 / (3,000/s) ≈ 333 s
where
t: the time between requests for a new block, in seconds (s)
block: IDs handed out per request, here 1 million
writes: links created per second across the fleet, here the 3,000/s peak
/s: per second
≈: approximately equal to (rounded)
In words: a million-ID block lasts about five and a half minutes at peak, so the coordinator sees about eleven block requests an hour across the fleet at steady peak, excluding the initial allocations and wasted ranges.
```

The multiply-and-wrap bijective shuffle from the "guessable" bullet looks like this:

```formula
m = (an) mod 62^7
where
n: the counter value, from 0 up to 62^7 − 1
a: a large constant that shares no factor with 62^7, so it is not a multiple of 2 or 31 (62 = 2 × 31)
mod: modulo, the remainder after division; it wraps the product back into the range 0 to 62^7 − 1
m: the shuffled value, which is then base62-encoded into the 7-character code
In words: multiply the counter by a fixed constant and keep the remainder; because the constant shares no factor with the size of the code space, no two counter values end up with the same code.
```

### Option D: Pre-generated key service

A key generation service pre-computes random 7-character codes, stores them in an "unused" table, and hands batches to write servers. It's essentially Option B with random rather than sequential codes. It works, but you have to store and manage billions of unused keys.

> [!tip] Recommended answer
> Range-allocated counters with a bijective shuffle, base62-encoded to 7 characters. Collision-free and short when ranges are never reused; the bijective shuffle is not an access-control mechanism, and the coordinator is touched only once per million links.

## Key takeaways

- Allocate non-overlapping ranges durably and never reuse them after crashes.
- A coprime multiply-and-wrap mapping preserves uniqueness.
- A bijection is not authorisation or proof of cryptographic security.

## Further reading

- [Python: numeric operations and divmod](https://docs.python.org/3/library/functions.html#divmod)
- [DynamoDB: conditional writes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html)
