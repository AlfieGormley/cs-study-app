---
id: fund-redundancy-failure-domains
title: Model redundancy with capacity and shared failures
level: intermediate
minutes: 5
summary: Calculate parallel and two-of-three availability, then test the independence, failover and survivor-capacity assumptions.
sourceLesson: fund-availability
---

Redundancy helps when another component can take over. Model that benefit using the survivors the workload actually needs, then account for failures that can affect every copy together.

## Components in parallel

If the system works as long as **at least one** of several redundant components works, they're in **parallel**. The system fails only if *all* fail, so work out the chance that every one is down and subtract it from 1:

```formula
A_total = 1 − (1 − A_1) × … × (1 − A_n)
A_total = 1 − ∏(1 − A_i)
where
A_total: the availability of the redundant group, as a fraction from 0 to 1
A_1, A_n: the availability of the first and last (n-th) component, each as a fraction
A_i: the availability of component number i, where i runs from 1 to n
1 − A_1: the unavailability of component 1, the fraction of time it is down
n: the number of redundant components
…: and so on: one factor for every component in between
∏: capital pi, "multiply together": the product of the bracket over every component i; the second line is just a compact way of writing the first
In words: the group is down only when every member is down at once, so multiply their down-fractions and subtract from 1.
```

```
            +--> [App 99%] --+
client ->LB-|                |-> ok
            +--> [App 99%] --+
```

```formula
A = 1 − (1 − A_s) × (1 − A_s)
A = 1 − (0.01 × 0.01)
A = 1 − 0.0001 = 0.9999 = 99.99%
where
A: the availability of the pair of app servers, as a fraction
A_s: the availability of one app server, 99% = 0.99, so it is down 1 − 0.99 = 0.01 of the time
In words: two servers that are each down 1% of the time are both down only 1% of 1% of the time.
```

Two 99% servers give 99.99%; three give 99.9999%. Redundancy is enormously powerful, which is why replication across availability zones is standard practice.

> [!warning] Redundancy needs spare capacity
> The parallel formula assumes **one survivor can carry the whole load**. If peak traffic needs both servers, losing either one at peak overloads the other, and the pair behaves like two components in series. Plan for **N+1** (or N+2): enough servers that the system still meets its load with one, or one zone, gone.

When some number of identical servers are needed out of a larger group (written "k of n"), the system is up while at least that many are up. For three 99% servers where any two can carry peak load, add up the chances of the states that work: all three up, or exactly two up.

```formula
P_3 = a^3 = 0.99^3 = 0.970299
P_2 = 3 × a^2 × (1 − a)
P_2 = 3 × 0.99^2 × 0.01 = 0.029403
A = P_3 + P_2 = 0.999702 ≈ 99.97%
where
P_3: the probability that all three servers are up
P_2: the probability that exactly two are up and one is down
a: the availability of one server, 0.99
^: "to the power of": a^3 means a × a × a
3: the number of ways to pick which one of the three servers is the one that is down
A: the availability of the tier, the probability at least two servers are up
≈: approximately equal to (rounded)
In words: the tier works when all three are up or when exactly one is down; add the probabilities of those two situations.
```

That's a big step down from the 99.9999% you'd get if any *one* could cope, and a big step up from the 97.03% of needing all three.

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
