---
id: cs1-feed-contract-graph-hydration
title: Connect feed APIs, social graph and hydration
level: advanced
minutes: 4
summary: Store posts once and keep identifiers in precomputed timelines.
sourceLesson: cs1-news-feed
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

- **Read-heavy**: assume 500 million posts and 3 billion timeline loads a day, about 6 loads per post, and each load shows dozens of posts, so far more posts are read than written.
- **Fast reads**: home timeline p99 under ~200 ms.
- **Eventually consistent**: a new post can take a few seconds to reach followers. But **read-your-writes**: an author must see their own post immediately.
- **Highly available**: a stale feed is better than an error.

Out of scope: search, DMs, trends, ads (we'll mention where ranking plugs them in).

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

Use **cursor pagination** (the cursor is the ID of the last post the client has seen), not offsets. New posts arrive at the top constantly, so "page 2" by offset would shift and show duplicates. Snowflake-style post IDs are roughly time-ordered (not a causal clock), so "older than this ID" is a natural cursor.

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

Timelines store **IDs, not post bodies**. A post shown to a million followers is stored once; edits and deletions change the canonical object rather than every timeline copy; serving caches still need a freshness policy.

## Key takeaways

- Store posts once and keep identifiers in precomputed timelines.
- Keep both following and follower indexes for different read paths.
- Use cursor pagination and durable publication of post-created work.

## Further reading

- [Meta: TAO social graph store](https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/)
- [X: recommendation pipeline repository](https://github.com/twitter/the-algorithm)
