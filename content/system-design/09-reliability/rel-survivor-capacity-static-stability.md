---
id: rel-survivor-capacity-static-stability
title: Survivor capacity and static stability
level: basic
minutes: 5
summary: Reserve enough existing capacity to survive planned failures without emergency provisioning.
sourceLesson: rel-designing-for-failure
---

Cells limit impact; redundancy keeps a serving path available. This unit assumes identical linear capacity and evenly redistributed work when calculating how busy the survivors become. Real load tests must also cover uneven work, peak demand and latency targets.

## Redundancy that actually works

Adding a second copy helps against failures not shared by all copies; full statistical independence is needed for the simple product-probability calculation. Two servers in the same rack share a power supply and a switch; two databases in the same region share a control plane; two replicas running the same buggy binary fail together.

| Redundancy | Protects against | Doesn't protect against |
|---|---|---|
| N+1 instances | One host dying | Bad deploy to all |
| Multi-AZ | Data-centre outage | Region control plane |
| Multi-region | Regional disaster | Global config error |
| Diverse software | Shared bug | Shared bad data |

### Active-active vs active-passive

- **Active-passive**: a standby takes over when the primary fails. Simple, but an unexercised standby may hide faults until failover; drills and validation reduce this risk, and failover itself can fail.
- **Active-active**: all copies serve traffic. Normal serving paths are exercised continuously; failure paths still need testing, but you must handle concurrent writes and must keep **enough headroom** that the survivors can absorb the load.

### Capacity for failure: N+1 and static stability

If you run 3 nodes at 80% utilisation and lose one, the remaining two need to carry 120% each. They fall over, and you have turned a single failure into a total outage. The total work stays the same when a node dies; it is just shared among fewer survivors:

```formula
U_after = (NU) / (N − k)
U_after = (3 × 80%) / (3 − 1)
U_after = 240% / 2 = 120%  ✗
U_after = (3 × 60%) / 2 = 90%  ✓
where
U_after: the utilisation of each surviving node after the failure, as a percentage of one node's capacity
N: the number of nodes before the failure, here 3
U: each node's utilisation before the failure, here 80% (or 60%)
k: the number of nodes that fail, here 1
%: per cent of one node's full capacity; above 100% the node is overloaded
✗ / ✓: overloaded / within capacity
In words: three nodes at 80% are doing 2.4 nodes' worth of work; split over two survivors that is 120% each, which they can't do. At 60% the survivors land on 90%, which they can.
```

Setting U_after to 100% and solving for U gives the general rule: the highest safe utilisation before a failure.

```formula
U_max = (N − k) / N
U_max = (3 − 1) / 3 = 2/3 ≈ 67%
U_max = (10 − 1) / 10 = 9/10 = 90%
where
U_max: the highest utilisation each node can run at and still let the survivors absorb the failed nodes' work without passing 100%
N: the number of nodes, here 3 (or 10)
k: the number of node failures the system must survive, here 1
≈: approximately equal to (rounded)
%: per cent of one node's capacity
In words: the fraction of nodes that survive is the fraction of capacity you can use. Three nodes surviving one loss can run at about 67%; ten nodes can run at 90%.
```

Treat U_max as a ceiling, not a target. At 60% the survivors land on 90%, and the queueing maths in the overload lesson shows that an illustrative M/M/1 model predicts mean response time ten times mean service time at 90%; this is not a universal latency multiplier. Real teams keep extra margin for traffic growth, uneven load balancing and the failure happening at peak. The rule also assumes load spreads evenly over the survivors.

More, smaller units make redundancy cheaper, as the second formula shows: 3 nodes surviving one loss can only run at 67%, but 10 nodes can run at 90%. The same logic is why three AZs are more efficient than two: two AZs that must each survive the other's loss can run at only 50%: one of two equal zones survives.

AWS calls the stronger version **static stability**: the system keeps working through a failure *without depending on new provisioning or impaired control-plane operations*, such as launching new instances or changing DNS. If you pre-provision capacity in each zone to survive losing another zone, you don't depend on a control plane that may itself be impaired during the event.

## Key takeaways

- Redundant copies need distinct failure exposure and regularly tested failover.
- Size survivors for the full redistributed load; the capacity ceiling assumes equal nodes and even work.
- Keep extra latency and traffic headroom below that ceiling. Static stability avoids impaired provisioning or management APIs.

## Further reading

- [Static stability using Availability Zones (AWS Builders' Library)](https://aws.amazon.com/builders-library/static-stability-using-availability-zones/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
