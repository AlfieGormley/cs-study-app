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

Candidate count multiplies the amount of model work. A cheap first stage can reduce how many candidates reach an expensive model, but its own feature lookups and scoring still cost resources. Measure the complete pipeline under representative batching, hardware and latency targets.

Actual batching, model architecture, hardware and utilisation change these inputs. Measure both stages under the same service-level target before translating GPU-equivalents into purchased machines. Under overload, a chronological cached page is a useful degradation path.

> [!analogy] Real-world analogy: A shortlist before detailed interviews
> A quick screening step narrows many applications before a smaller group receives a detailed assessment.
>
> **How it maps:** Candidate generation and light scoring reduce expensive model evaluations.
>
> **Where it stops:** Early screening can discard relevant items, so measure recall and bias as well as saved computation; this analogy is not evidence for a hiring process.

## Key takeaways

- Separate candidate gathering, feature lookup, light scoring and heavy scoring.
- Normalised accelerator capacity is an assumption to measure.
- Prune candidates and cache ranked pages while preserving visibility checks.

## Further reading

- [Meta: how machine learning powers News Feed ranking](https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/)
- [X: recommendation pipeline repository](https://github.com/twitter/the-algorithm)
