---
id: prob-idle-servers-inversions
title: Count empty servers and inversions
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Random assignment leaves many servers idle even with one job per server on average.
---

## Example: idle servers

A load balancer assigns n jobs to n servers (at least one of each), each job independently to a uniformly random server. How many servers get no job?

Each job misses a given server unless it chooses that one server. Independence lets us multiply the avoidance probabilities across all jobs. Add one indicator per server:

```formula
E[Z] = n × (1 − 1/n)^n
E[Z] ≈ n / e ≈ 0.368 × n
E[Z] = 100 × 0.99^100 ≈ 36.6
where
Z: the number of idle servers (servers that receive no job)
E[Z]: the expected (long-run average) number of idle servers
n: the number of jobs and of servers; 100 in the last line
(1 − 1/n)^n: the chance one server is missed by all n jobs
e: Euler's number, about 2.718, the base of natural logarithms; (1 − 1/n)^n gets closer to 1/e as n grows
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: about 37% of servers sit idle when jobs are thrown at them uniformly at random.
```

With 100 jobs and 100 servers, the expected number of idle servers is about 36.6; other servers may receive one or several jobs. Random assignment is far from balanced, which motivates the **power of two choices** technique: in the sequential model with n unit jobs, n initially empty servers, independent uniform candidate choices and current load information, picking the less loaded of two candidates dramatically reduces the maximum load with high probability as n grows. Real scheduling systems need their own workload and measurement assumptions.

## Example: inversions and insertion sort

An **inversion** (array inversion) in an array is a pair of positions where the earlier element is bigger than the later one. The adjacent-swap version of insertion sort performs exactly one swap per inversion; the usual shifting version instead performs one rightward shift per inversion. For a uniformly random permutation of distinct values, each pair is equally likely to be in either order, so each is inverted with probability 1/2.

```formula
E[N_inv] = C(n, 2) × 1/2
E[N_inv] = (n(n − 1)) / 4
E[N_inv] = (100 × 99) / 4 = 2,475
where
N_inv: the number of inversions, pairs of positions i < j with a[i] > a[j]
n: the length of the array; 100 in the last line
a[i]: the element at position i
C(n, 2): "n choose 2", the number of pairs of positions, n × (n − 1) / 2
E[ ]: expected value
1/2: the chance a given pair is inverted
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: half of all pairs are inverted on average, so insertion sort does about n²/4 swaps on a random input.
```

For an array of 100 elements that is 2,475 swaps on average. Using **Θ** (big-Theta, "grows exactly as fast as, up to constant factors") with n the array length, that is Θ(n²) even in the average case, only half the worst case.

## The same indicator recipe for hash buckets

Treat each independently assigned key as a job and each bucket as a server. One indicator per key counts occupancy; one per bucket counts emptiness; one per unordered pair of keys counts collisions. For a fixed pair, after its first key lands, the second matches its bucket with probability one divided by the bucket count.

```formula
E[K_0] = n / m
E[Z] = m(1 − 1/m)^n
E[N_c] = (n(n − 1)) / (2m)
where
n: the nonnegative integer number of independently assigned keys
m: the positive integer number of equally likely buckets
K_0: the number of keys in one specified bucket
Z: the number of empty buckets
N_c: the number of unordered pairs of distinct keys assigned the same bucket
E[ ]: expected value, averaging the count over assignments
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: add the corresponding indicator probabilities to find occupancy, empty buckets and colliding pairs; maximum occupancy is a different quantity.
```

## Key takeaways
- Random assignment leaves many servers idle even with one job per server on average.
- Count pairs to find expected inversions and hash collisions.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
