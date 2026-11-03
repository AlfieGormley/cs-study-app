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

Posts create background work; timeline loads create foreground reads. Their timing and cost differ, so measure each path and its peak independently.

Now the number that drives the design. If a post reaches an assumed average of **200 eligible followers** and we push each post into every follower's timeline:

```formula reference
I = P F
where
I: expected timeline inserts over the chosen interval
P: posts in that interval
F: mean number of eligible recipient timelines per post, weighted by the posts actually created
In words: fan-out work grows with the number of posts and the eligible recipients of each post; an unweighted follower count per account can misestimate it.
```

Fan-out can be parallelised, but hot keys, duplicates and shared resources still matter. Keep an explicit cache cap, such as the latest 800 identifiers, and measure the actual representation:

Timeline memory depends on how many users have cached timelines, how many identifiers each retains, entry representation and copies. Raw identifier bytes exclude object and allocator overhead.

This raw payload budget calls for measured cluster sizing, including overhead, failover and rebuild traffic; keep timelines only for *active* users.

> [!note] Content gap: historical Twitter deployment figures
> The linked presentation page identifies the speaker and topic but did not provide a readable transcript verifying the exact historical request rates, delivery times and compute savings. Those deployment figures are omitted; the calculations in this lesson use explicitly hypothetical inputs.

Post storage, at about 1 KB per post (text plus metadata; media lives in object storage):

Store canonical post bodies and media separately from derived timelines. Retention, indexes, replicas and recovery costs belong in that storage budget.

## Key takeaways

- Use eligible recipients per post rather than an unweighted account average.
- Distinguish raw timeline payload from Redis overhead and replicas.
- Measure node throughput instead of treating the illustrative capacity as a benchmark.

## Further reading

- [Meta: TAO social graph store](https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/)
- [Meta: News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
