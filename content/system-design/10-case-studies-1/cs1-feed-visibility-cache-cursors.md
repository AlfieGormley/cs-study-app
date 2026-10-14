---
id: cs1-feed-visibility-cache-cursors
title: Re-check visibility while hydrating cached timelines
level: advanced
minutes: 4
summary: Derived IDs are candidates; current permission state decides visibility.
sourceLesson: cs1-news-feed
---

## Deep dive 3: Follows, unfollows, blocks and deletes

Precomputed timelines are a cache of a *derived* view, so every change to the inputs has to reach them. Interviewers love probing this.

- **Follow**: the new followee's recent posts aren't in your timeline. Backfill asynchronously: fetch their last ~50 posts and merge them into your list. Until it completes, the timeline service can pull that account at read time.
- **Unfollow**: their posts are still in your list. Rather than scanning and rewriting it, filter at hydration ("is the author still followed?"), using a cached copy of your following set, and let the old IDs age out of the capped list.
- **Block or mute**: same approach, filter at read time, with an explicit freshness mechanism for the permission cache; merely consulting a stale cached set does not make the change immediate.
- **Protected (private) accounts**: if an author locks their account, hydration must re-check visibility for each post, not trust what fan-out decided earlier.
- **Delete**: mark the post deleted once; hydration drops it (see below). For legal takedowns, also invalidate serving caches and enforce an authoritative takedown state; a best-effort cache purge alone does not prove every replica is fresh.

The principle: **fan-out decides what *might* be shown; hydration decides what *may* be shown.** Every permission and visibility check happens at read time, against current state.

## Deep dive 4: Timeline caching

The timeline cache is a Redis cluster sharded by `user_id`. Replayed fan-out events need idempotent inserts; LPUSH alone can add duplicates and asynchronous arrival order is not necessarily post order:

- Each timeline is a capped list (`LPUSH` then `LTRIM 0 799`) or a sorted set scored by an exactly representable timestamp, with the full post ID encoded as a fixed-width member for tie-breaking. Redis scores are double-precision floats, so do not put arbitrary 64-bit Snowflake IDs directly into the score.
- Replicate for availability. Losing a shard isn't data loss, since timelines can be rebuilt from the posts store and social graph, but rebuilding millions at once would hammer the databases, so keep replicas.
- **Cache miss** (new or returning user): build from a captured boundary while buffering or replaying concurrent fan-out, then merge/deduplicate before switching to live updates. A blind rebuild can overwrite concurrent inserts.
- **Hydration** is a second cache layer: `post_id → post` in Memcached or Redis. A timeline of 50 posts becomes one multi-get. Hot posts (a viral tweet in millions of timelines) are served from cache; add a small in-process cache for the very hottest.
- **Deletions**: fanning out a delete to 50M timelines is expensive. Instead, mark the post deleted and let hydration drop it. The dead ID ages out of the capped list naturally.
- **Read-your-writes**: merge the author's acknowledged post into their own view while fan-out proceeds asynchronously. A server-side guarantee also needs fresh hydration and a fallback when a cache is lost or stale; optimistic client insertion improves that client's UI only.
- **Scrolling past the cap**: the list holds only 800 IDs. A user who scrolls beyond it gets older pages built by pull (or from a slower, disk-backed store). Few users ever scroll that far, which is why the cap works.
- **Cursor stability**: because the cursor is a post ID ("older than X"), new posts ahead of that immutable order do not cause offset shifts. Late-arriving older IDs can still be missed; ranked feeds need a cursor that points into a saved copy of the ranking rather than only a post ID.

## Key takeaways

- Derived IDs are candidates; current permission state decides visibility.
- Keep replayed inserts and cache rebuilds race-safe.
- Enforce read-your-writes separately from asynchronous fan-out.
- A stable chronological cursor still needs a policy for late arrivals.

## Further reading

- [Meta: News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
- [Meta: TAO social graph store](https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/)
- [Redis: sorted set score precision](https://redis.io/docs/latest/commands/zadd/)
