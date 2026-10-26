---
id: prob-total-probability
title: Weight cases with total probability
level: basic
minutes: 3
sourceLesson: prob-basics
summary: A partition covers every outcome exactly once.
---

An overall error rate depends on both regional error rates and how much traffic each region serves. Giving a tiny region the same weight as a busy one answers the wrong question.

## Weight cases by how often they occur

A **partition of the sample space** separates outcomes into disjoint cases that cover everything exactly once. The **law of total probability** finds an overall chance by weighting its chance within each case by the chance of that case. Zero-probability cases can be omitted; a finite or countable partition supports this sum.

If most requests go to a reliable region, the overall rate lies nearer that region's rate. Moving more traffic to an unreliable region raises the overall error rate even if neither regional rate changes.

```formula reference
P(A) = Σ_i P(A | B_i) × P(B_i)
where
P: probability of measurable events, dimensionless and between zero and one
P(A): the overall probability of event A
B_i: the i-th piece of the partition, for example "the request went to region i"
i: an index counting the pieces 1, 2, 3, …
Σ_i: sigma, "add up the following term for every piece i"
P(A | B_i): the probability of A given that we are in piece B_i (| is read "given")
P(B_i): the probability of landing in piece B_i
In words: the overall event probability is a weighted average of its probability within each disjoint case, weighted by how often each case occurs.
```

The cases must refer to the same experiment and cover it without overlap. Averaging regional percentages equally would instead describe a uniformly selected region.

## The observation policy matters

In the three-door game, a car is initially equally likely behind each door. After your choice, a knowledgeable host always reveals an unchosen goat and offers a switch. Switching wins whenever your original choice was wrong: two out of three games.

If the host also chooses fairly when two goat doors are available, switching still has a two-thirds chance after observing a particular door opened. To condition on that observation, weight each car location by how likely that location makes the host's action.

A host who opens an unchosen door blindly and happens to reveal a goat follows a different policy. Under uniform blind choice, the two unopened doors are equally likely conditional on that observation. The visible goat alone does not specify the experiment.

## Key takeaways
- Weight conditional rates by the size of each disjoint case.
- A changed mixture can change an overall rate without changing any component rate.
- Include the observation policy in the probability model.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
