---
id: fund-dependency-availability
title: Calculate the availability of a request path
level: intermediate
minutes: 4
summary: Multiply required dependencies in series, combine redundant groups, and remove optional work from the critical path.
sourceLesson: fund-availability
---

The previous unit modelled redundant components in parallel. A real request usually also needs several different tiers to work together, so its availability combines both kinds of relationship.

## Components in series

If a request needs **every** component to work, the components are in **series**. Assuming independent failures, the chance that all of them are up at once is the product of their availabilities:

```formula
A_total = A_1 × A_2 × … × A_n
where
A_total: the availability of the whole chain, as a fraction from 0 to 1
A_1, A_2, A_n: the availability of the first, second and last (n-th) component, each as a fraction (99.9% = 0.999)
n: the number of components the request needs
…: and so on: one factor for every component in between
In words: the chain is up only when every link is up, so multiply the links' availabilities together.
```

```
client -> [LB] -> [App] -> [DB]
         99.99%  99.9%   99.95%
```

```formula
A = A_LB × A_App × A_DB
A = 0.9999 × 0.999 × 0.9995
A ≈ 0.99840 ≈ 99.84%
where
A: the end-to-end availability of the chain, as a fraction
A_LB: the load balancer's availability, 99.99% = 0.9999
A_App: the app tier's availability, 99.9% = 0.999
A_DB: the database's availability, 99.95% = 0.9995
≈: approximately equal to (rounded)
In words: multiplying three high availabilities gives one that is lower than any of them.
```

The chain is **less** available than its weakest link. Every synchronous dependency you add lowers the ceiling. With independent failures, a service requiring 10 dependencies at 99.9% each has modelled availability of 0.999 raised to the power 10, about 0.990 (99.0%), i.e. about 3.65 days of downtime a year.

This is the mathematical reason to:

- Remove dependencies from the critical path (do work asynchronously).
- Degrade gracefully: show the page without recommendations rather than failing it.
- Be suspicious of deep synchronous microservice call chains.

## Combining them

Real systems mix both. Compute parallel groups first, then multiply the groups in series:

```formula
A_LB = 1 − 0.001^2 = 0.999999
A_App = 1 − 0.01^3 = 0.999999
A_DB = 1 − 0.005^2 = 0.999975
A = A_LB × A_App × A_DB
A ≈ 0.999973 ≈ 99.997%
where
A_LB: the availability of a pair of load balancers, each 99.9% available (down 0.001 of the time)
A_App: the availability of three app servers, each 99% available (down 0.01 of the time), where any one can carry the load
A_DB: the availability of a pair of databases, each 99.5% available (down 0.005 of the time)
A: the availability of the whole system, the three groups in series
^: "to the power of": 0.001^2 means 0.001 × 0.001
≈: approximately equal to (rounded)
In words: work out each redundant group with the parallel formula, then multiply the groups together because a request needs all three.
```

## Key takeaways
- A request needing every independent dependency has availability equal to the product of their availabilities.
- Calculate each parallel group first, then multiply required groups in series.
- Asynchronous work and graceful degradation reduce the dependencies that must succeed for the core request.

## Further reading
- [Availability and Beyond (AWS)](https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/availability-and-beyond-improving-resilience.html)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
