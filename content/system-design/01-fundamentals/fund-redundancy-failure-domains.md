---
id: fund-redundancy-failure-domains
title: Model redundancy with capacity and shared failures
level: intermediate
minutes: 4
summary: Explain how redundancy depends on independent failures, working failover and enough survivor capacity.
sourceLesson: fund-availability
---

Redundancy helps when another component can take over. Model that benefit using the survivors the workload actually needs, then account for failures that can affect every copy together.

## Components in parallel

If the system works as long as **at least one** of several redundant components works, they're in **parallel**. The system fails only if *all* fail, so work out the chance that every one is down and subtract it from 1:

```formula reference
A_total = 1 − (1 − A_1)(1 − A_2)
where
A_total: availability of a pair when either member alone can carry the load, as a fraction from 0 to 1
A_1, A_2: availability of the first and second member, each as a fraction from 0 to 1
In words: either member can keep the service running, so the pair is unavailable only when both are down. This estimate assumes independent failures and immediate, successful failover.
```

```
            +--> [App 99%] --+
client ->LB-|                |-> ok
            +--> [App 99%] --+
```

For two independent 99%-available servers, with immediate switching and either able to carry the load, the model gives 99.99% availability. A third reduces the chance of all being down further. The gain depends on those assumptions.

> [!warning] Redundancy needs spare capacity
> The parallel formula assumes **one survivor can carry the whole load**. If peak traffic needs both servers, losing either one at peak overloads the other, and the pair behaves like two components in series. Plan for **N+1** (or N+2): enough servers that the system still meets its load with one, or one zone, gone.

When some number of identical servers are needed out of a larger group (written "k of n"), the system is up while at least that many are up. For three 99% servers where any two can carry peak load, add up the chances of the states that work: all three up, or exactly two up.

For three independent 99%-available servers where any two can carry the load, the model gives about 99.97% availability. This is lower than the any-one-of-three case because states with only one survivor now count as failures.

The useful question is which survivor combinations can actually serve peak traffic, rather than how many copies exist.

## The big caveat: independence

The formulas above assume failures are **independent**. In reality, they often aren't:

- Two servers in the same rack share a power supply and switch.
- Replicas running the same software share the same bugs (a bad deploy or a leap-second bug takes them all out at once).
- A bad config push hits every region.
- Failover itself can fail, or take minutes. The parallel formula assumes switching is instant; a 5-minute failover that happens four times a year is 20 minutes of downtime the formula never shows.

Two 99% servers on the same host don't give you 99.99%. This is why cloud providers offer **availability zones** (separate power, cooling and networking) and why multi-region designs exist. It's also why staged rollouts matter: they stop a single bad change from becoming a correlated failure.

> [!warning] Redundancy you haven't tested is a hope, not a design
> A standby database that has never been failed over to is likely to surprise you. Practise failovers regularly (game days, chaos engineering).

## Key takeaways
- Parallel availability improves only when surviving components can serve the required load.
- Two-of-three capacity has different availability from any-one-of-three capacity.
- Shared power, software, config and slow failover invalidate the simplest independent, instant-switch model.

## Further reading
- [Availability and Beyond (AWS)](https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/availability-and-beyond-improving-resilience.html)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
