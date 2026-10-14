---
id: rel-cells-shuffle-isolation
title: Cells and shuffle-shard isolation
level: basic
minutes: 3
summary: Calculate shuffle-shard overlap and limit the customer blast radius.
sourceLesson: rel-designing-for-failure
---

A single point of failure can disable the entire service. A fault boundary instead contains damage to a host, zone, region or cell. This unit asks how much damage one bad tenant or change can cause, even when the service remains partly available.

## Blast radius

Redundancy stops a failure taking *everything* down. **Blast radius** asks the next question: when something does fail, how many users or requests are affected?

Techniques for shrinking it:

- **Cell-based architecture**: split the service into independent full copies (cells), each serving a slice of customers. A bad deploy or poison request takes out one cell, not all of them. AWS uses cell-based architecture widely for this reason. The thin routing layer that maps customers to cells is shared by all of them, so it must be kept as simple and static as possible.
- **Shuffle sharding**: give each customer a random subset of workers. A customer who sends poison requests only damages their own subset. The number of different subsets ("shuffle shards") is a combination count (see the formula below).
- **Availability zones and regions** as fault boundaries, so a power or network event is contained.
- **Staged rollouts**: deploy to one host, then one zone, then one region (covered in the deployments lesson).

How much does shuffle sharding help? Count the distinct subsets a customer could be given. Choosing k workers out of n, where order doesn't matter, is the "n choose k" count:

```formula
S = C(n, k) = n! / (k! × (n − k)!)
S = C(8, 2) = (8 × 7) / (2 × 1)
S = 56 / 2 = 28
where
S: the number of distinct worker subsets (shuffle shards) available
C(n, k): "n choose k", the number of ways to pick k items from n when order doesn't matter
n: the total number of workers, here 8
k: the number of workers given to each customer, here 2
!: factorial; 4! = 4 × 3 × 2 × 1 = 24
In words: with 8 workers and 2 per customer there are 28 different pairs, so a randomly chosen other customer has only a 1 in 28 chance (about 3.6%) of sharing both workers with a poisonous customer.
```

Customers who share just *one* worker still have a healthy second worker and can continue at reduced capacity if retry/rerouting and survivor headroom support it. The calculation assumes shards are assigned at random and that a customer survives as long as one of its workers is healthy.

> [!example] Shuffle sharding in numbers
> AWS has described Route 53 shuffle sharding over 2,048 virtual name servers, giving each domain 4 of them. The number of possible combinations, 2,048 choose 4, is about 730 billion, so an attack against one customer's servers almost never fully overlaps another's.

## Key takeaways

- A cell contains a full serving stack for a slice of customers.
- Keep the shared cell router simple because every cell depends on it.
- Eight workers assigned in random pairs provide 28 possible shards; partial overlap can still degrade service.

## Further reading

- [Workload isolation using shuffle-sharding (AWS Builders' Library)](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/)
- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
