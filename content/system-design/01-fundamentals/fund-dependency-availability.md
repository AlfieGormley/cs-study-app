---
id: fund-dependency-availability
title: Find availability risks along a request path
level: intermediate
minutes: 3
summary: Identify required dependencies, distinguish redundant alternatives, and move optional work off the critical path.
sourceLesson: fund-availability
---

The previous unit modelled redundant components in parallel. A real request usually also needs several different tiers to work together, so its availability combines both kinds of relationship.

## Components in series

If a request needs **every** component to work, the components are in **series**. Assuming independent failures, the chance that all of them are up at once is the product of their availabilities:

```formula reference
A_total = A_1 × A_2 × … × A_n
where
A_total: the availability of the whole chain, as a fraction from 0 to 1
A_1, A_2, A_n: the availability of the first, second and last (n-th) component, each as a fraction (99.9% = 0.999)
n: the number of components the request needs
…: and so on: one factor for every component in between
In words: the chain works only when every required link works. With independent failures, multiplying their availabilities estimates how often they all work together.
```

```
client -> [LB] -> [App] -> [DB]
         99.99%  99.9%   99.95%
```

In this example, all three tiers must be healthy. Their independent modelled availability is about 99.84%, below each individual tier.

A required dependency creates another way for the request to fail. The chain cannot be more available than its least available required tier; with independent imperfect tiers it is less available. Adding synchronous dependencies therefore consumes the request path's reliability budget.

This is the mathematical reason to:

- Remove dependencies from the critical path (do work asynchronously).
- Degrade gracefully: show the page without recommendations rather than failing it.
- Be suspicious of deep synchronous microservice call chains.

## Combining them

Real systems mix both. Compute parallel groups first, then multiply the groups in series:

First identify the redundant alternatives inside each tier. Check that survivors have capacity and that failover works. Then treat the tiers the request still needs as a chain. Redundant app servers do not remove the database as a required dependency, and a shared failure can still affect several tiers together.

## Key takeaways
- A request needing every independent dependency has availability equal to the product of their availabilities.
- Calculate each parallel group first, then multiply required groups in series.
- Asynchronous work and graceful degradation reduce the dependencies that must succeed for the core request.

## Further reading
- [Availability and Beyond (AWS)](https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/availability-and-beyond-improving-resilience.html)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
