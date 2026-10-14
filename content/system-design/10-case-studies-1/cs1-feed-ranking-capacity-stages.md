---
id: cs1-feed-ranking-capacity-stages
title: Control ranking cost with candidate stages
level: advanced
minutes: 3
summary: Separate candidate gathering, feature lookup, light scoring and heavy scoring.
sourceLesson: cs1-news-feed
---

The chronological feed already has identifiers and hydrated posts. Ranking adds model inference to that path, so its cost must be sized independently from Redis reads.

## Deep dive 5: Ranking

A "For you" feed replaces reverse-chronological order with predicted relevance. Modern feeds are a pipeline:

1. **Candidate generation**: gather perhaps 1,000–2,000 candidates: the user's precomputed timeline (in-network) plus recommended posts from accounts they don't follow (out-of-network, from embeddings or graph-based recommenders). X's published repository demonstrates candidate sourcing, ranking and filtering stages. The candidate budget here is illustrative.
2. **Feature hydration**: for each candidate, fetch features: author affinity, post age, engagement so far, media type.
3. **Scoring**: a lightweight model prunes to a few hundred, then a heavier neural network predicts probabilities of like, reply, repost, dwell, and negative feedback, combined into one score. The exact historical X parameter count is omitted: the linked engineering article was unavailable during this audit, and the retrieved repository overview does not establish that number.
4. **Filtering and heuristics**: remove blocked or muted authors and unsafe content, enforce author diversity (not five posts in a row from one account), mix in ads.
5. **Serve and log**: impressions and engagement feed back into training.

Ranking changes the cost model: you're now doing ML inference over a thousand candidates per request. That's why ranking services cache scored feeds briefly and why "pull to refresh" may return a precomputed ranked page.

## A concrete capacity model

Assume 90,000 feed requests per second, 1,500 candidates each, and 0.2 milliseconds of normalised additive GPU capacity per candidate. This cost already includes the chosen batching strategy; it is a hypothetical input, not a hardware benchmark.

```formula
g = 90,000/s × 1,500 × 0.0002 s
g = 27,000 s/s
h = 90,000/s × 300 × 0.0002 s
h = 5,400 s/s
l = 90,000/s × 1,500 × 0.00001 s
l = 1,350 s/s
total = h + l = 6,750 s/s
where
g: GPU-equivalent capacity for scoring every candidate with the heavy model
h: heavy-model capacity after pruning to 300 candidates
l: light-model capacity on all candidates at an assumed 0.01 milliseconds each
total: combined capacity of the two-stage model
s: seconds; s/s means seconds of normalised GPU work per elapsed second
In words: pruning cuts the heavy stage fivefold; counting the cheap first stage too cuts total assumed capacity fourfold.
```

Actual batching, model architecture, hardware and utilisation change these inputs. Measure both stages under the same service-level target before translating GPU-equivalents into purchased machines. Under overload, a chronological cached page is a useful degradation path.

## Key takeaways

- Separate candidate gathering, feature lookup, light scoring and heavy scoring.
- Normalised accelerator capacity is an assumption to measure.
- Prune candidates and cache ranked pages while preserving visibility checks.

## Further reading

- [Meta: how machine learning powers News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
- [X: recommendation pipeline repository](https://github.com/twitter/the-algorithm)
