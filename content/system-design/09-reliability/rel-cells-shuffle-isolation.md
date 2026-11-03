---
id: rel-cells-shuffle-isolation
title: Cells and shuffle-shard isolation
level: basic
minutes: 3
summary: Explain partial overlap between worker subsets and limit the customer blast radius.
sourceLesson: rel-designing-for-failure
---

A single point of failure can disable the entire service. A fault boundary instead contains damage to a host, zone, region or cell. This unit asks how much damage one bad tenant or change can cause, even when the service remains partly available.

## Blast radius

Redundancy stops a failure taking *everything* down. **Blast radius** asks the next question: when something does fail, how many users or requests are affected?

Techniques for shrinking it:

- **Cell-based architecture**: split the service into independent full copies (cells), each serving a slice of customers. A bad deploy or poison request takes out one cell, not all of them. AWS uses cell-based architecture widely for this reason. The thin routing layer that maps customers to cells is shared by all of them, so it must be kept as simple and static as possible.
- **Shuffle sharding**: give each customer a random subset of workers. A customer who sends poison requests only damages their own subset. Subsets can overlap, so a damaged worker may affect several tenants without disabling all their workers.
- **Availability zones and regions** as fault boundaries, so a power or network event is contained.
- **Staged rollouts**: deploy to one host, then one zone, then one region (covered in the deployments lesson).

A small example shows why overlapping subsets differ from fixed disjoint shards:

Eight workers assigned in random pairs provide 28 possible subsets. Another uniformly assigned tenant has a one-in-28 chance of sharing the poisoned pair completely. Partial overlap is more common.

Customers who share just *one* worker still have a healthy second worker and can continue at reduced capacity if retry/rerouting and survivor headroom support it. The calculation assumes shards are assigned at random and that a customer survives as long as one of its workers is healthy.

> [!example] Shuffle sharding in numbers
> AWS has described Route 53 shuffle sharding over 2,048 virtual name servers, giving each domain 4 of them. The number of possible combinations, 2,048 choose 4, is about 730 billion, so an attack against one customer's servers almost never fully overlaps another's.

> [!analogy] Real-world analogy: separate buildings with a shared entrance map
> Damage in one self-contained building need not close every building on a site. Visitors still depend on the map that sends them to the right one.
>
> **How it maps:** Each building corresponds to a cell serving its assigned customers; the shared map corresponds to the cell router.
>
> **Where it stops:** Software faults can cross intended boundaries through shared dependencies or retries. Isolation must be designed and tested, not assumed from a diagram.

## Key takeaways

- A cell contains a full serving stack for a slice of customers.
- Keep the shared cell router simple because every cell depends on it.
- Eight workers assigned in random pairs provide 28 possible shards; partial overlap can still degrade service.

## Further reading

- [Workload isolation using shuffle-sharding (AWS Builders' Library)](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/)
- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
