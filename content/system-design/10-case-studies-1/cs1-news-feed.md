---
id: cs1-news-feed
title: Design a news feed like Twitter/X
level: advanced
minutes: 21
summary: Design a home timeline for hundreds of millions of users, weighing fan-out on write against fan-out on read, solving the celebrity problem with a hybrid, caching timelines in Redis and adding ML ranking.
---

The news feed is the classic read-heavy social problem. Users post rarely and read constantly. Each read needs the recent posts from everyone they follow, merged and ordered, in under a couple of hundred milliseconds.

The central design question is **when to do the merging**: when a post is written (push it into every follower's feed) or when a feed is read (pull from everyone the reader follows). A useful answer for the workload assumed here is a hybrid, and explaining why is the heart of this interview.

## Step 1: Requirements

**Functional**

- Users publish posts (assume a 280-character product limit, optionally media).
- Users follow other users (one-directional, like X; not mutual like Facebook friends).
- **Home timeline**: posts from accounts you follow, newest first, with an optional ranked "For you" mode.
- **User timeline**: one user's own posts.
- Infinite scroll (pagination).

**Non-functional**

- **Read-heavy**: perhaps 100 timeline reads per post written.
- **Fast reads**: home timeline p99 under ~200 ms.
- **Eventually consistent**: a new post can take a few seconds to reach followers. But **read-your-own-writes**: an author must see their own post immediately.
- **Highly available**: a stale feed is better than an error.

Out of scope: search, DMs, trends, ads (we'll mention where ranking plugs them in).

## Step 2: Estimates

Assume **300 million DAU**, **500 million posts/day** (a hypothetical workload), and each user loads their home timeline **10 times/day**.

```
Post writes:  500M / 10^5 s  ≈ 5,000/s
              (peak x3)      ≈ 15,000/s
Feed reads:   3B / 10^5 s    ≈ 30,000/s
              (peak x3)      ≈ 90,000/s
```

Now the number that drives the design. If a post reaches an assumed average of **200 eligible followers** and we push each post into every follower's timeline:

```
Fan-out writes: 500M x 200 = 100B/day
              ≈ 1M timeline inserts/s
```

That's a lot, but it's simple, parallel work: appending an 8-byte ID to a list in Redis. At an explicitly assumed 100k appends/s per node, 1M/s would consume ten nodes at full utilization before peaks or headroom. This is arithmetic, not a Redis benchmark. Timeline cache size, storing the latest **800** post IDs per active user (an assumed cache cap), at an assumed 16-byte raw payload per entry (post ID + author ID), excluding Redis object/allocator overhead:

```
300M x 800 x 16 B  ≈ 3.8 TB
x3 replicas        ≈ 11.5 TB of RAM
```

Big, but a large Redis cluster can hold it, and we only keep timelines for *active* users.

> [!note] Content gap: historical Twitter deployment figures
> The linked presentation page identifies the speaker and topic but did not provide a readable transcript verifying the exact historical request rates, delivery times and compute savings. Those deployment figures are omitted; the calculations in this lesson use explicitly hypothetical inputs.
Post storage: 500M × ~1 KB (text plus metadata; media lives in object storage) ≈ 500 GB/day, ~180 TB/year.

## Step 3: API

```
POST /v1/posts {text, mediaIds[]}
  -> 201 {postId}

GET /v1/timeline/home
    ?cursor=<postId>&limit=50&mode=latest
  -> {posts:[...], nextCursor}

GET /v1/users/{id}/posts?cursor=...
POST   /v1/users/{id}/follow
DELETE /v1/users/{id}/follow
```

Use **cursor pagination** (`cursor = last post ID seen`), not offsets. New posts arrive at the top constantly, so "page 2" by offset would shift and show duplicates. Snowflake-style post IDs are roughly time-ordered (not a causal clock), so "older than this ID" is a natural cursor.

## Step 4: Data model

```
posts            (shard by post_id)
  post_id  (Snowflake, time-ordered)
  author_id, text, media_ids
  created_at, deleted

user_posts       (shard by author_id)
  author_id, post_id   -> user timeline

follows          (two tables)
  followers(followee_id -> follower_id)
  following(follower_id -> followee_id)

home_timeline    (Redis, by user_id)
  user_id -> [post_id, ...] capped 800
```

The social graph is stored both ways because fan-out asks "who follows X?" and pull asks "whom does Y follow?". Meta's published TAO and Twitter's historical FlockDB are examples of purpose-built graph stores for exactly these lookups.

Likes, reply and repost counts change constantly; keep them in a separate counter service rather than rewriting post rows.

## Step 5: High-level design

```
          Client
            |
            v
       API gateway
        |        |
        v        v
    Post svc   Timeline svc
     |   |       |      |
     v   |       v      v
 Posts   |   Timeline  Post
 store   |   cache     cache
         v   (Redis)
       Kafka     ^
         |       |
         v       |
   Fan-out workers
         |
         v
   Social graph
```

**Write path**: the post service stores the post and a `PostCreated` outbox entry in one transaction, then relays the event to Kafka with retries. Fan-out workers look up the author's followers and append the post ID to each follower's timeline list in Redis.

**Read path**: the timeline service reads the user's list of IDs from Redis, then **hydrates** them: a multi-get of post objects from the post cache, plus author profiles and counters. It returns fully formed posts.

Timelines store **IDs, not post bodies**. A post shown to a million followers is stored once; edits and deletions only touch one object.

## Deep dive 1: Fan-out on write vs fan-out on read

### Fan-out on write (push)

When a post is created, insert its ID into every follower's precomputed timeline.

- **Reads are trivial**: one Redis list read plus hydration. Fast and predictable.
- **Writes are amplified**: one post becomes N writes, where N is the follower count.
- **Wasted work**: you update timelines of followers who won't log in today.
- **Lag for big accounts**: fan-out to millions of followers takes time.

### Fan-out on read (pull)

Store posts only in the author's user timeline. At read time, fetch recent posts from everyone the reader follows and merge them.

- **Writes are trivial**: one insert.
- **Reads are expensive**: a user following 1,000 accounts needs 1,000 lookups (or a scatter-gather across shards) and a k-way merge, on *every* timeline load. At 90,000 reads/s, that's up to 90 million lookups per second.
- **Latency is unpredictable**: the slowest of 1,000 lookups sets the response time.

### Which to choose?

Reads outnumber writes heavily, and most accounts have modest follower counts, so **push is the default**. Pull's cost lands on the hot path (reads) while push's cost lands off it (async workers). This example uses push to shift work off timeline reads; the actual choice also depends on follower distribution, posting rates and active readers.

## Deep dive 2: The celebrity problem

Pure push breaks for accounts with enormous followings. An account with **50 million followers** turns one post into 50 million Redis inserts:

```
50M inserts / 1M inserts/s ≈ 50 s
```

...and that's if the entire fan-out fleet does nothing else. Several celebrities posting at once (a sports final, an election) would back up everyone's feeds for minutes. Slow fan-out also caused ordering bugs: a reply from a follower who received the post early could be fanned out *before* the original reached followers further down the list.

### The hybrid

1. **Classify accounts.** Above a threshold (say, 1 million followers, or tuned by measured cost), an account is a "celebrity". Its posts are **not fanned out**.
2. **Push for everyone else.** Normal accounts keep fan-out on write.
3. **Pull celebrities at read time.** When building a timeline, the timeline service reads the precomputed list *and* fetches recent posts from the (few) celebrities this user follows, then merges them.

The pull side is cheap because:

- A user follows only a handful of celebrities, so it's a few extra lookups, not 1,000.
- Celebrity user timelines are read by millions of users, so they're always hot in cache.

### Other refinements

- **Skip inactive followers.** Don't fan out to users who haven't logged in for, say, 30 days. If they return, rebuild their timeline with a pull from their followings, then switch them back to push.
- **Prioritise fan-out**: process followers who are online right now first.
- **Per-relationship tuning**: a celebrity's post to followers who interact with them constantly might still be pushed.

Changing the push/pull classification needs overlap and deduplication so posts are neither missed nor shown twice during the transition.

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

- Each timeline is a capped list (`LPUSH` then `LTRIM 0 799`) or a sorted set scored by an exactly representable timestamp, with the full post ID encoded as a fixed-width member for tie-breaking. Redis scores are doubles, so do not put arbitrary 64-bit Snowflake IDs directly into the score.
- Replicate for availability. Losing a shard isn't data loss, since timelines can be rebuilt from the posts store and social graph, but rebuilding millions at once would hammer the databases, so keep replicas.
- **Cache miss** (new or returning user): build from a captured boundary while buffering or replaying concurrent fan-out, then merge/deduplicate before switching to live updates. A blind rebuild can overwrite concurrent inserts.
- **Hydration** is a second cache layer: `post_id → post` in Memcached or Redis. A timeline of 50 posts becomes one multi-get. Hot posts (a viral tweet in millions of timelines) are served from cache; add a small in-process cache for the very hottest.
- **Deletions**: fanning out a delete to 50M timelines is expensive. Instead, mark the post deleted and let hydration drop it. The dead ID ages out of the capped list naturally.
- **Read-your-own-writes**: the post service synchronously inserts the author's new post into their own timeline (or the client inserts it optimistically), so they never wonder whether their post worked.
- **Scrolling past the cap**: the list holds only 800 IDs. A user who scrolls beyond it gets older pages built by pull (or from a slower, disk-backed store). Few users ever scroll that far, which is why the cap works.
- **Cursor stability**: because the cursor is a post ID ("older than X"), new posts ahead of that immutable order do not cause offset shifts. Late-arriving older IDs can still be missed; ranked feeds need a ranking/snapshot cursor rather than only a post ID.

## Deep dive 5: Ranking

A "For you" feed replaces reverse-chronological order with predicted relevance. Modern feeds are a pipeline:

1. **Candidate generation**: gather perhaps 1,000–2,000 candidates: the user's precomputed timeline (in-network) plus recommended posts from accounts they don't follow (out-of-network, from embeddings or graph-based recommenders). X's published repository demonstrates candidate sourcing, ranking and filtering stages. The candidate budget here is illustrative.
2. **Feature hydration**: for each candidate, fetch features: author affinity, post age, engagement so far, media type.
3. **Scoring**: a lightweight model prunes to a few hundred, then a heavier neural network predicts probabilities of like, reply, repost, dwell, and negative feedback, combined into one score. The exact historical X parameter count is omitted: the linked engineering article was unavailable during this audit, and the retrieved repository overview does not establish that number.
4. **Filtering and heuristics**: remove blocked or muted authors and unsafe content, enforce author diversity (not five posts in a row from one account), mix in ads.
5. **Serve and log**: impressions and engagement feed back into training.

Ranking changes the cost model: you're now doing ML inference over a thousand candidates per request. That's why ranking services cache scored feeds briefly and why "pull to refresh" may return a precomputed ranked page.

## Bottlenecks and trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Push | Fast reads | Write amplification |
| Pull | Cheap writes | Slow, costly reads |
| Hybrid | Best of both | Two code paths |
| IDs in timeline | One copy of post | Hydration step |

Other bottlenecks:

- **Fan-out backlog** during global events. Monitor Kafka consumer lag and autoscale workers; degrade by fanning out only to active users.
- **Hot posts** in the post cache. Replicate hot keys or add local caches.
- **Graph lookups** for users with millions of followers: page through followers in batches, splitting the fan-out into many independent tasks.

## At 10x scale

At 3 billion DAU and 5 billion posts/day:

- Fan-out becomes ~10M inserts/s, and timeline RAM grows to ~38 TB before replication. **Lower the celebrity threshold** so more posts are pulled, and fan out only to recently active followers.
- **Multi-region**: keep timeline caches in the user's home region. Replicate posts globally (asynchronously) so hydration is local.
- **Tiered timelines**: keep only the most recent ~200 IDs in RAM and older pages on SSD-backed stores.
- **Ranking cost dominates**: precompute candidate pools offline, use cheaper first-stage models, and run heavy models on GPUs only for the top few hundred candidates.
- **Graceful degradation**: under extreme load, serve the chronological cached timeline without ranking rather than failing.

## Key takeaways

- The feed is read-heavy, so precompute: fan-out on write makes reads a single cache lookup.
- Fan-out cost is posts × average followers; with 200 followers, 500M posts/day is ~1M inserts/s.
- Pure push fails for celebrities; use a hybrid: push for normal accounts, pull for huge accounts at read time.
- Store post IDs in timelines and hydrate from a post cache; deletions and edits then touch one object.
- Skip inactive users during fan-out and rebuild their timelines on return.
- Fan-out decides what might be shown; hydration re-checks deletes, unfollows, blocks and privacy against current state.
- Ranking adds a candidate generation → scoring → filtering pipeline, and makes inference cost a first-class concern.

## Further reading

- [InfoQ: Timelines at Scale (Raffi Krikorian, Twitter)](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/)
- [High Scalability: the architecture Twitter uses to deal with 150M active users](https://highscalability.com/the-architecture-twitter-uses-to-deal-with-150m-active-users/)
- [System Design Primer: design the Twitter timeline and search](https://github.com/donnemartin/system-design-primer/blob/master/solutions/system_design/twitter/README.md)
- [Meta engineering: how machine learning powers News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
- [TAO: Facebook's distributed data store for the social graph (USENIX ATC '13)](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson)
- [X's open-sourced recommendation algorithm (GitHub)](https://github.com/twitter/the-algorithm)
