---
id: cs1-feed-backlog-tiered-growth
title: Manage fan-out backlog and tier timeline storage
level: advanced
minutes: 3
summary: Observe consumer lag and protect active readers during spikes.
sourceLesson: cs1-news-feed
---

The hybrid feed still has an asynchronous fan-out fleet, a timeline cache and ranking capacity. Apply the earlier workload estimates to the next bottlenecks: queue lag, hot posts, graph paging and growing RAM demand.

## Bottlenecks and trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Push | Fast reads | Write amplification |
| Pull | Cheap writes | Slow, costly reads |
| Hybrid | Tunes work to account size | Two code paths and migration complexity |
| IDs in timeline | One copy of post | Hydration step |

Other bottlenecks:

- **Fan-out backlog** during global events. Monitor Kafka consumer lag and autoscale workers; degrade by fanning out only to active users.
- **Hot posts** in the post cache. Replicate hot keys or add local caches.
- **Graph lookups** for users with millions of followers: page through followers in batches, splitting the fan-out into many independent tasks.

## At 10x scale

At 3 billion DAU and 5 billion posts/day:

- The assumed fan-out and timeline-memory budgets grow substantially. **Lower the celebrity threshold** so more posts are pulled, and fan out only to recently active followers.
- **Multi-region**: keep timeline caches in the user's home region. Replicate posts globally (asynchronously) so hydration is local.
- **Tiered timelines**: keep only the most recent ~200 IDs in RAM and older pages on SSD-backed stores.
- **If ranking cost dominates**: precompute candidate pools offline, use cheaper first-stage models, and run heavy models on GPUs only for the top few hundred candidates.
- **Graceful degradation**: under extreme load, serve the chronological cached timeline without ranking rather than failing.

Growing posts and active users increase different costs: fan-out work and cached timeline memory. Monitor queue age, the number of active timelines, entries retained and rebuild demand before choosing the next optimisation.

## Key takeaways

- Observe consumer lag and protect active readers during spikes.
- Lower the push threshold only with a safe overlap and deduplication plan.
- Keep shallow hot pages in RAM and rebuild deeper or returning-user pages.

## Further reading

- [X: recommendation pipeline repository](https://github.com/twitter/the-algorithm)
- [Meta: News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
