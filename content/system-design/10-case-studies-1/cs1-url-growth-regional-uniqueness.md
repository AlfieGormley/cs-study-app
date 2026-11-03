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

- **Seven characters is no longer enough** for 10 years (3.65 trillion links vs 3.5 trillion codes). Move to 8 characters (218 trillion) for new links. An 8-character string can never equal a 7-character one, so new generated links use exactly eight characters (left-pad short encodings), with a fresh permutation over all 218 trillion 8-character values. Also revise alias reservations or atomically skip already-claimed aliases.
- **Storage reaches petabytes** (about 1.8 PB raw over 10 years). Move cold links to cheaper storage if latency permits; expire them only when the retention contract allows it.
- **Go multi-region.** Replicate mapping rows asynchronously to serve redirects locally, with a separate freshness policy for deletion and blocking. Durable disjoint ID ranges avoid cross-region coordination on each generated-code create while unused ranges remain. A fresh mapping can be missing elsewhere until replication catches up; a reachable home-region fallback can resolve that miss.
- **Push redirects to the edge.** CDN workers (Cloudflare Workers, Lambda@Edge) can hold hot mappings and reduce origin work; end-to-end latency still needs measurement, shipping click logs back in batches.
- **Shard the analytics pipeline** by code and pre-aggregate at the edge before sending upstream.

The revised forecast needs about 3.65 trillion codes, exceeding the roughly 3.52 trillion seven-character space. The storage budget also grows, but it remains a separate constraint from identifier capacity.

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
