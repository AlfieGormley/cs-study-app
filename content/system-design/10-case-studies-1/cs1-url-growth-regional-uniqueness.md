---
id: cs1-url-growth-regional-uniqueness
title: Expand the namespace and preserve regional uniqueness
level: intermediate
minutes: 3
summary: Seven characters cannot hold ten years at a billion new links a day.
sourceLesson: cs1-url-shortener
---

Now increase the assumed workload tenfold: one billion new links a day and 300,000 redirects a second. Earlier units established cache freshness and non-reused ID ranges; apply both when expanding the namespace and serving regions.

## At 10x scale

At 1 billion new links a day and 300k redirects/s:

- **Seven characters is no longer enough** for 10 years (3.65 trillion links vs 3.5 trillion codes; see the sum below). Move to 8 characters (218 trillion) for new links. An 8-character string can never equal a 7-character one, so new generated links use exactly eight characters (left-pad short encodings), with a fresh permutation over all 218 trillion 8-character values. Also revise alias reservations or atomically skip already-claimed aliases.
- **Storage reaches petabytes** (about 1.8 PB raw over 10 years). Expire links nobody has clicked for years, or move them to cheaper storage.
- **Go multi-region.** Redirects are read-only and links are immutable, so replicate the links store asynchronously to every region and serve redirects locally. Give each region its own ID ranges so regions never need to coordinate on writes. A link created in Europe might take a second to resolve in Asia; the primary-fallback from deep dive 5 covers that window.
- **Push redirects to the edge.** CDN workers (Cloudflare Workers, Lambda@Edge) can hold hot mappings and reduce origin work; end-to-end latency still needs measurement, shipping click logs back in batches.
- **Shard the analytics pipeline** by code and pre-aggregate at the edge before sending upstream.

The two 10x sums:

```formula
links = 1 bn × 365 × 10 = 3.65 × 10^12
62^7 ≈ 3.52 × 10^12
storage = 3.65 × 10^12 × 500 B ≈ 1.8 PB
where
links: links created over 10 years at 1 billion a day
bn: billion (10^9)
62^7: the number of 7-character base62 codes
storage: raw bytes for those links at about 500 bytes each
B: bytes
PB: petabyte, 10^15 bytes (1,000 terabytes)
10^12: a trillion
≈: approximately equal to (rounded)
In words: ten years at a billion links a day needs slightly more codes than seven characters provide, and about 1.8 petabytes of raw storage.
```

## Distinguish generated codes from aliases

A region can create generated links during a bounded network partition while it still owns unused, durable ranges. It must stop or reject creation when its range is exhausted; disconnected regions cannot safely allocate the same new range. Custom aliases are different because a user can request the same text in two regions. Route that uniqueness decision to a home authority, or reject and defer alias creation while the authority is unreachable.

Asynchronous replicas support local redirect reads with a documented freshness delay. A fallback to the home region improves a fresh-link miss only when that region is reachable. Abuse blocking and deletions need a separate propagation or authoritative check policy; immutable destinations do not make these changes instantly consistent.

## Key takeaways

- Seven characters cannot hold ten years at a billion new links a day.
- Use an exact new code length and revisit alias reservations.
- Disjoint preallocated ranges support partitioned creation; custom aliases still need global uniqueness.

## Further reading

- [DynamoDB: conditional writes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html)
- [Python: numeric operations and divmod](https://docs.python.org/3/library/functions.html#divmod)
