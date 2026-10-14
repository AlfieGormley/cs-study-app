---
id: cs1-feed-push-pull-celebrity-hybrid
title: Choose push and pull for ordinary and huge accounts
level: advanced
minutes: 4
summary: Push shifts repeated read work into asynchronous fan-out.
sourceLesson: cs1-news-feed
---

## Deep dive 1: Fan-out on write vs fan-out on read

### Fan-out on write (push)

When a post is created, insert its ID into every follower's precomputed timeline.

- **Reads are trivial**: one Redis list read plus hydration. Fast and predictable.
- **Writes are amplified**: one post becomes one write per follower.
- **Wasted work**: you update timelines of followers who won't log in today.
- **Lag for big accounts**: fan-out to millions of followers takes time.

### Fan-out on read (pull)

Store posts only in the author's user timeline. At read time, fetch recent posts from everyone the reader follows and merge them.

- **Writes are trivial**: one insert.
- **Reads are expensive**: a user following 1,000 accounts needs 1,000 lookups (or a scatter-gather across shards) and a k-way merge (combining 1,000 sorted lists into one), on *every* timeline load. At 90,000 reads/s, that's up to 90,000 × 1,000 = 90 million lookups per second.
- **Latency is unpredictable**: the slowest of 1,000 lookups sets the response time.

### Which to choose?

Reads outnumber writes heavily, and most accounts have modest follower counts, so **push is the default**. Pull's cost lands on the hot path (reads) while push's cost lands off it (async workers). This example uses push to shift work off timeline reads; the actual choice also depends on follower distribution, posting rates and active readers.

## Deep dive 2: The celebrity problem

Pure push breaks for accounts with enormous followings. An account with **50 million followers** turns one post into 50 million Redis inserts:

```formula
t = followers / rate
t = 50M / (1M/s) = 50 s
where
t: time to finish fanning out one post, in seconds (s)
followers: timelines to insert into, 50 million
rate: the fan-out fleet's total insert rate, 1 million per second
M: million
/s: per second
In words: even with the whole fleet working on nothing else, one celebrity post takes about 50 seconds to reach every follower.
```

...and that's if the entire fan-out fleet does nothing else. Several celebrities posting at once (a sports final, an election) would back up everyone's feeds for minutes. Slow fan-out can also cause visible arrival inversions: a reply from a follower who received the post early could be fanned out *before* the original reached followers further down the list.

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

## Key takeaways

- Push shifts repeated read work into asynchronous fan-out.
- Huge follower counts can occupy the fleet and reorder visible arrival.
- Pull huge accounts on reads and deduplicate while changing classification.

## Further reading

- [Meta: TAO social graph store](https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/)
- [X: recommendation pipeline repository](https://github.com/twitter/the-algorithm)
