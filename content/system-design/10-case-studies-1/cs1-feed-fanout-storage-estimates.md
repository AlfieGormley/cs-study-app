---
id: cs1-feed-fanout-storage-estimates
title: Estimate post amplification and timeline memory
level: advanced
minutes: 4
summary: Use eligible recipients per post rather than an unweighted account average.
sourceLesson: cs1-news-feed
---

The feed API stores posts and hydrates identifier lists. This unit estimates how much copying and memory that design implies under a hypothetical 300-million-user workload.

## Step 2: Estimates

Assume **300 million DAU**, **500 million posts/day** (a hypothetical workload), and each user loads their home timeline **10 times/day**.

Feed reads per day are users times loads each: 300M × 10 = 3B. Then convert to per second and apply an assumed peak factor of 3:

```formula
posts = 500M / (10^5 s) ≈ 5,000/s
peak posts = 5,000/s × 3 = 15,000/s
reads = 3B / (10^5 s) ≈ 30,000/s
peak reads = 30,000/s × 3 = 90,000/s
where
posts, reads: average posts written and home-timeline loads per second
peak posts, peak reads: the same at the busiest time
M: million (10^6)
B: billion (10^9)
10^5: 100,000, the seconds in a day (86,400) rounded up
s: seconds; /s means per second
≈: approximately equal to (rounded)
In words: half a billion posts a day is about 5,000 a second, and three billion timeline loads a day is about 30,000 a second, both tripled at peak.
```

Now the number that drives the design. If a post reaches an assumed average of **200 eligible followers** and we push each post into every follower's timeline:

```formula
inserts = posts × f
inserts = 500M × 200 = 100B/day
rate = 100B / (10^5 s) ≈ 1M/s
nodes = 1M/s / (100k/s) = 10
where
inserts: timeline inserts per day, one for each follower of each post
posts: posts written per day, 500 million
f: the average number of eligible followers per post, an assumed 200
rate: timeline inserts per second
nodes: Redis nodes needed at full use, if one node handles an assumed 100,000 appends per second
M: million
B: billion
k: thousand
day: one day; /day means per day
10^5: 100,000, the seconds in a day rounded
s: seconds; /s means per second
≈: approximately equal to
In words: every post is copied into 200 timelines, so 500 million posts a day become 100 billion inserts a day, about a million a second, which would keep ten fully busy nodes occupied.
```

That's a lot, but it's simple, parallel work: appending compact identifiers to a timeline structure. At an explicitly assumed 100k appends/s per node, 1M/s would consume ten nodes at full utilization before peaks or headroom. This is arithmetic, not a Redis benchmark. Timeline cache size, storing the latest **800** post IDs per active user (an assumed cache cap), at an assumed 16-byte raw payload per entry (post ID + author ID), excluding Redis object/allocator overhead:

```formula
cache = users × entries × size
cache = 300M × 800 × 16 B ≈ 3.8 TB
total = (300M × 800 × 16 B) × 3
total = 11.52 TB ≈ 11.5 TB
where
cache: raw timeline-cache memory, before Redis overhead
users: active users with a cached timeline, 300 million
entries: post IDs kept per timeline, the assumed cap of 800
size: bytes per entry, an assumed 16 (post ID + author ID)
total: memory with 3 copies of every timeline (three copies total)
M: million
B: bytes
TB: terabyte, 10^12 bytes
≈: approximately equal to (rounded)
In words: 300 million timelines of 800 16-byte entries is about 3.8 TB, or about 11.5 TB of RAM when stored three times.
```

This raw payload budget calls for measured cluster sizing, including overhead, failover and rebuild traffic; keep timelines only for *active* users.

> [!note] Content gap: historical Twitter deployment figures
> The linked presentation page identifies the speaker and topic but did not provide a readable transcript verifying the exact historical request rates, delivery times and compute savings. Those deployment figures are omitted; the calculations in this lesson use explicitly hypothetical inputs.

Post storage, at about 1 KB per post (text plus metadata; media lives in object storage):

```formula
daily = 500M × 1 KB = 500 GB
yearly = 500 GB × 365 ≈ 180 TB
where
daily, yearly: new post data per day and per year
M: million
KB: kilobyte, 1,000 bytes
GB: gigabyte, 10^9 bytes
TB: terabyte, 10^12 bytes
≈: approximately equal to (rounded)
In words: half a billion 1 KB posts is 500 GB a day, about 180 TB a year.
```

## Key takeaways

- Use eligible recipients per post rather than an unweighted account average.
- Distinguish raw timeline payload from Redis overhead and replicas.
- Measure node throughput instead of treating the illustrative capacity as a benchmark.

## Further reading

- [Meta: TAO social graph store](https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/)
- [Meta: News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
