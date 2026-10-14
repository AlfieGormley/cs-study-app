---
id: fund-scaling-state
title: Choose scaling strategies and expose hidden state
level: intermediate
minutes: 5
summary: Compare scale-up with scale-out, and identify the state that prevents an app instance being safely replaced.
sourceLesson: fund-scalability
---

A system is **scalable** if it can handle more load by adding resources, while keeping performance acceptable and cost roughly proportional to load.

"Load" can mean many things: requests per second, number of users, data volume, write rate or number of concurrent connections. Always ask "scalable along *which* dimension?". A system that handles 10x more reads may not handle 10x more writes.

## Vertical scaling (scale up)

Make the machine bigger: more CPU cores, more RAM, faster disks.

**Pros**

- Usually no application changes. A bigger Postgres instance remains one Postgres instance, although configuration and resource limits may need adjustment.
- No distributed-systems problems: no network partitions between nodes, no consistency puzzles.
- Surprisingly far-reaching. Cloud instances with hundreds of vCPUs and multiple terabytes of RAM are readily available.

**Cons**

- **A ceiling.** Eventually there's no bigger machine.
- **Cost at the top end.** On your own hardware, the biggest servers cost disproportionately more per unit of capacity. Cloud prices vary by instance family, region and purchase model. A continuously running fixed-size instance must be paid for even during quiet periods; compare current prices rather than assuming a universal cost curve.
- **A single point of failure.** One big machine is still one machine.
- **Downtime to resize**, in many setups.

> [!tip] Don't dismiss scaling up
> Stack Overflow famously served huge traffic from a handful of powerful SQL Server machines for years. Scaling up is often the cheapest, simplest first move, especially for databases. A common path is: scale the database up, add read replicas and a cache for reads, and shard only when *writes* outgrow the biggest sensible machine.

## Horizontal scaling (scale out)

Add more machines and spread the load across them.

**Pros**

- Near-unlimited capacity, if the workload partitions well.
- Redundancy comes naturally: losing one of 20 nodes loses 5% of capacity.
- Commodity hardware and elastic autoscaling.

**Cons**

- Requires load balancing, service discovery and distributed coordination.
- Data must be partitioned or replicated, which brings consistency trade-offs.
- More moving parts to operate and debug.

```
 vertical             horizontal

 +--------+       +--+ +--+ +--+ +--+
 |        |       |  | |  | |  | |  |
 |  BIG   |       +--+ +--+ +--+ +--+
 |        |            ^
 +--------+       load balancer
```

## Stateless vs stateful

The single most important property for horizontal scaling is whether a component is **stateless**.

A **stateless** service keeps no client-specific data between requests. Any instance can handle any request. Session data, uploaded files and caches live in shared external stores (a database, Redis, S3).

```
          +--> [app 1] --+
client -> LB-> [app 2] ---> Redis / DB
          +--> [app 3] --+
```

Why stateless services are easy to scale:

- Add or remove instances freely; the load balancer needs no stickiness.
- An instance crash loses nothing except in-flight requests.
- Autoscaling, rolling deploys and spot instances become easier, but still require graceful shutdown, retry-safe requests and sufficient capacity in backing services.

This is the "processes" factor of the Twelve-Factor App: processes are stateless and share nothing; state lives in backing services.

A **stateful** component holds data that matters: databases, caches, message brokers, WebSocket connection servers, game servers. Scaling them needs answers to:

- **Where does each piece of data live?** (partitioning, or sharding)
- **How are copies kept in sync?** (replication)
- **What happens when a node joins, leaves or dies?** (rebalancing, failover)

These are the hard problems covered in the databases, consistency and messaging modules. A common architecture pattern is to **push state down** into a few well-understood stateful systems (Postgres, Redis, Kafka, S3) and keep everything above them stateless.

> [!warning] Hidden state
> In-memory authoritative sessions, unpersisted local uploads and uncoordinated rate-limit counters create hidden correctness-critical state. Disposable local caches can be compatible with a stateless service when correctness does not depend on their contents. Symptoms: users logged out randomly, rate limits that are 10x too lenient with 10 instances.

## Key takeaways
- Name the load dimension you need to scale: reads, writes, data or connections.
- Scaling up keeps a simpler architecture; scaling out adds coordination and data-placement work.
- Keep correctness-critical state in appropriate backing services; disposable caches differ from authoritative local state.

## Further reading
- [The Twelve-Factor App: Processes](https://12factor.net/processes)
- [Scalability](https://en.wikipedia.org/wiki/Scalability)
