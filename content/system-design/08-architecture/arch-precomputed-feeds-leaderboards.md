---
id: arch-precomputed-feeds-leaderboards
title: Precomputing feeds and leaderboards
level: intermediate
minutes: 3
summary: Move repeated query work ahead of reads while accounting for fan-out skew and ranking semantics.
sourceLesson: arch-scaling-reads
---

Stored read models can go further: maintain the answer before anybody asks. This works best when the repeated read cost outweighs the maintenance work.

## Precomputation

Taken further, you compute the answer **before anyone asks**:

- **Fan-out on write for feeds**: when someone posts, push the post ID into each follower's precomputed timeline (in Redis). Reading a feed becomes one list fetch. Twitter used this approach for most users.
- **Leaderboards**: maintain a Redis sorted set updated on each score change, rather than sorting millions of rows per request.
- **Rollups**: hourly and daily aggregate tables for dashboards instead of scanning raw events.
- **Search autocomplete**: precomputed top-N completions per prefix.

> [!warning] Precomputation has an edge case
> Fan-out on write breaks for celebrities. A user with 50 million followers would trigger 50 million timeline writes per post. Twitter's hybrid approach: fan out on write for normal users, and merge celebrity posts in at read time.

## Choosing a technique

| Problem | First reach for |
|---|---|
| DB CPU from reads | Cache, replicas |
| Expensive joins | Denormalise |
| Expensive aggregates | Materialised view |
| Same answer for all | CDN / precompute |
| Per-user heavy query | Precompute per user |

Usually you combine them: replicas behind a cache, serving denormalised tables, with the heaviest aggregates precomputed.

### Ranking is part of the contract

A Redis sorted set can maintain player scores incrementally and serve the top players or a member's rank, rather than sorting the full population on every request. Define tie-breaking: equal scores use member ordering, which must match the product's chosen rule. A database index ordered by score and a stable tie-breaker can improve the top-100 query, but that alone does not make every player's exact global rank cheap. A periodically cached top list cannot satisfy a live personalised rank requirement without another suitable rank path.

## Key takeaways
- Precomputation turns repeated expensive reads into stored answers or incremental updates.
- Fan-out on write needs a celebrity threshold and a hybrid read path to avoid enormous per-post work.
- Choose ranking structures for the required top results, personal rank and deterministic ties.
- Combine replicas, caches and stored views according to the bottleneck rather than choosing one technique universally.

## Further reading
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Redis: Sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/)
