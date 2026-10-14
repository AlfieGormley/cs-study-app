---
id: arch-autoscaling-shared-bottlenecks
title: Scaling ahead of shared bottlenecks
level: basic
minutes: 3
summary: Choose scaling signals, allow for readiness delay and budget database connections as instances grow.
sourceLesson: arch-stateless-web-tier
---

Replacement makes automatic scaling possible, but it does not make capacity arrive immediately. The goal is to keep admitted work within every tier's sustainable capacity.

## Autoscaling

With stateless servers you can let a controller adjust the count to match load. Typical signals:

- **CPU utilisation**: simple and widely used; choose a target from load testing and required headroom; 50–70% is an illustrative starting range, not a universal optimum.
- **Requests per second per instance**: better when the work is I/O-bound and CPU stays low.
- **Queue depth**: for workers, scale on the number of messages waiting.
- **Schedules**: scale up before a known peak (9 am logins, a 7 pm TV advert).

Autoscaling isn't instant. VM provisioning, image pulls and application warm-up all take time; measure readiness time for the actual workload rather than assuming a VM/container timing range. If traffic can double in 30 seconds, autoscaling alone won't save you. Keep a baseline buffer, use predictive or scheduled scaling, and shed load gracefully.

> [!warning] Scaling the web tier can break the database
> Going from 10 to 100 app servers, each with a pool of 20 database connections, takes you from 200 to 2,000 connections. Whether that exceeds limits or sustainable load depends on database configuration, memory and active query demand. Use a connection pooler (PgBouncer, RDS Proxy) and remember the bottleneck usually moves down a tier.

Every app server keeps its own pool of open database connections, so the total the database sees grows with the server count:

```formula
C = N × P
C = 100 × 20 = 2000
where
C: the total number of connections opened against the database
N: the number of app server instances, here 100 (up from 10)
P: the size of each server's connection pool, here 20
In words: ten times the servers means ten times the database connections: 10 × 20 = 200 becomes 100 × 20 = 2,000.
```

This is the upper bound when every pool is full. Putting a pooler such as PgBouncer between the app servers and the database lets many client connections share far fewer real database connections.

## Containers

A **container** packages an application and its dependencies into an image for a supported platform; host kernel, architecture, configuration and external services still affect behavior. Unlike a VM, it shares the host's kernel, which can reduce some virtualization overhead. Time to serving readiness still depends on the runtime, image availability, initialization and dependencies.

Containers suit stateless services: an image is immutable, any copy is interchangeable, and you replace them rather than patch them.

## Key takeaways
- Use metrics that represent the actual bottleneck and keep capacity ready before predictable bursts.
- An instance count multiplied by its full pool size bounds requested database connections.
- Containers package dependencies but readiness still depends on images, initialisation and backing services.
- Pool connections and bound or shed excess work before autoscaling moves overload into another tier.

## Further reading
- [Kubernetes: Overview](https://kubernetes.io/docs/concepts/overview/)
