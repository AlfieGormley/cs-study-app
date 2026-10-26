---
id: prob-records-coupons
title: Find harmonic expectations for records and coverage
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: A record at a given position has reciprocal-position probability.
---

Random sampling makes discovery easy at first and harder later. Two common examples are finding a new record while scanning values and visiting every shard by random probing.

## Records become less frequent

```python
def scan(a):
    best = float("-inf")
    updates = 0
    for x in a:
        # Count only new record values.
        if x > best:
            best = x
            updates += 1
    return updates
```

This function counts new running maxima, not comparisons. It examines every item even when no new record occurs.

For a uniformly random permutation of distinct finite values, each of the first few positions is equally likely to contain their largest value. The first position always sets a record; later positions have progressively smaller record chances. Adding one indicator per position gives a **harmonic number**, which grows logarithmically with input length.

This describes the average number of record updates. Ascending input updates every time; descending input updates only at the start. Neither ordering is representative of all uniform permutations.

## Complete coverage gets progressively harder

In the **coupon collector** model, each request independently selects one of a fixed positive number of equally likely shards, with replacement. Early requests often find a new shard. Near the end, most requests revisit known shards.

Break the process into stages. Within a stage, the set of missing shards is fixed, so the wait for a new one is geometric. As that set shrinks, the chance of progress falls and the expected stage wait rises. Add the stage means to find the expected total; it grows like shard count times its logarithm.

The final missing shard alone takes one shard-count's worth of requests on average. One request per shard therefore does not imply complete coverage. If coverage is required and the list is known, deliberately visiting each shard avoids this random repetition.

## Key takeaways
- Record updates are rarer later, although the scan still examines every item.
- Random coverage slows as fewer unseen targets remain.
- Uniform sampling with replacement is different from a planned traversal.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
