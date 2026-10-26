---
id: prob-idle-servers-inversions
title: Count empty servers and inversions
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Random assignment leaves many servers idle even with one job per server on average.
---

An average of one job per server does not mean each server receives one job. Independent uniform assignment allows repeats, leaving some servers idle while others receive several jobs.

## Ask one question per server

For a fixed server to be idle, every job must miss it. Under independent assignments those avoidance probabilities multiply. Add one empty-server indicator per server to obtain the expected number idle.

With 100 jobs independently assigned to 100 equally likely servers, about 37 servers are idle on average. The total work still averages one job per server; that average says nothing about the fullest server. Sampling two candidate servers and choosing the less loaded can improve balance under an appropriate sequential allocation model with current load information.

## Ask one question per pair

An **inversion** is a pair of positions where the earlier value exceeds the later value. In a uniformly random permutation of distinct values, each pair is equally likely to be in either order. Half the pairs are therefore inverted on average.

Adjacent-swap insertion sort removes one inversion per swap; the usual shifting implementation makes one rightward shift per inversion. Because the number of pairs grows quadratically with array length, so does average insertion-sort work on these random permutations. Nearly sorted inputs with few inversions behave differently.

## Transfer the method to hashing

Keys assigned independently to uniform buckets behave like jobs assigned to servers. A specified bucket's expected occupancy, the number of empty buckets and the number of colliding key pairs are three different quantities.

A bucket with three keys contains three colliding pairs, not one. Pair counts can exceed bucket counts. The maximum occupancy is not a sum of per-bucket occupancies, so linearity does not directly give its expectation.

## Key takeaways
- Average occupancy does not describe imbalance or the maximum.
- Choose indicators for the quantity actually being counted.
- Pairs explain both inversions and collisions.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
