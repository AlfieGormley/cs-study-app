---
id: fund-scalability
title: Scalability, statelessness, Amdahl's and Little's laws
level: intermediate
minutes: 12
summary: Vertical vs horizontal scaling, why stateless services scale easily and stateful ones don't, and two laws that bound what scaling can achieve.
---

A system is **scalable** if it can handle more load by adding resources, while keeping performance acceptable and cost roughly proportional to load.

"Load" can mean many things: requests per second, number of users, data volume, write rate or number of concurrent connections. Always ask "scalable along *which* dimension?". A system that handles 10x more reads may not handle 10x more writes.

## Vertical scaling (scale up)

Make the machine bigger: more CPU cores, more RAM, faster disks.

**Pros**

- No code changes. A bigger Postgres instance is still one Postgres instance.
- No distributed-systems problems: no network partitions between nodes, no consistency puzzles.
- Surprisingly far-reaching. Cloud instances with hundreds of vCPUs and multiple terabytes of RAM are readily available.

**Cons**

- **A ceiling.** Eventually there's no bigger machine.
- **Cost at the top end.** On your own hardware, the biggest servers cost disproportionately more per unit of capacity. In the cloud, price per vCPU is roughly linear within an instance family, but the largest high-memory machines are specialist and expensive, and you pay for peak size around the clock.
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

## Amdahl's law: the limit of parallelism

Some part of almost every job can only be done one step at a time (it is **serial**); the rest can be split across workers (it is **parallel**). Gene Amdahl pointed out in 1967 that the serial part limits how much faster extra workers can make the job. Measure the job's time on one worker as 1; the serial share still takes the same time, while the parallel share is divided between the workers:

```formula
S(N) = 1 / ((1 − p) + p / N)
S_max = 1 / (1 − p)
where
S(N): the speed-up with N workers: how many times faster the job runs than on one worker
N: the number of workers (cores, machines) sharing the parallel part
p: the parallel fraction, the share of the one-worker running time that can be split between workers, from 0 to 1
1 − p: the serial fraction, the share that must run on one worker whatever happens
S_max: the limit of S(N) as N grows without bound (infinitely many workers): the parallel term p / N shrinks to 0
In words: the speed-up is the original time divided by the new time, and the new time can never drop below the serial part, so the serial part caps the speed-up.
```

Example: with a parallel fraction of 0.95 and 10 workers, the speed-up is 1 / (0.05 + 0.095) = 1 / 0.145 ≈ 6.9x. With unlimited workers the cap is 1 / 0.05 = 20x. The law assumes the job's size stays fixed and that splitting the work costs nothing; real coordination costs make things worse (see the USL below).

| Parallel part p | Max speed-up |
|---|---|
| 50% | 2x |
| 90% | 10x |
| 95% | 20x |
| 99% | 100x |

With 95% parallel, even infinite workers give only 20x. The serial part dominates.

In system design, a shared bottleneck may play a similar limiting role. These components are not necessarily single-threaded, but each has finite capacity:

- A single primary database that handles all writes.
- A global lock or a single-threaded sequencer.
- A single coordinator service.

Amdahl tells you that adding app servers won't help once you're bottlenecked on one of these. You must remove or partition the serial component.

> [!note] Universal Scalability Law
> Real systems often do worse than Amdahl, because nodes must coordinate (cache coherence, cross-node chatter). Neil Gunther's USL models two costs: **contention** (queueing for a shared resource, which is Amdahl's serial part) and **coherence** (nodes keeping each other up to date). Coherence cost grows roughly with the number of node *pairs*, which grows much faster than the number of nodes (formula below), so it can make throughput *fall* as you add nodes.
>
> The shapes are diagnostic. A curve that rises then **flattens** points to contention: find the shared bottleneck. A curve that rises then **falls** points to coherence: look for all-to-all chatter, global locks or broadcast cache invalidation.

The number of pairs among a group of nodes is:

```formula
P = N × (N − 1) / 2 ≈ N^2 / 2
N = 8: P = 8 × 7 / 2 = 28
N = 16: P = 16 × 15 / 2 = 120
where
P: the number of distinct node pairs, each a pair that may need to exchange coordination messages
N: the number of nodes in the cluster
N^2: N squared, N × N
≈: approximately equal to (close for large N)
In words: each of the N nodes can pair with the N − 1 others, and dividing by 2 stops each pair being counted twice. Doubling the nodes roughly quadruples the pairs.
```

Gustafson's law gives the optimistic counterpart: as you add machines you usually also grow the *problem* (more users, more data), so the parallel portion grows and scaling stays useful.

## Little's law: concurrency, throughput, latency

Little's law is one of the most useful equations in capacity planning. For any stable system (one where the queue doesn't grow forever), averaged over a long enough time:

```formula
L = λ × W
where
L: the average number of items in the system at once (requests in flight, busy threads, open connections); a plain count
λ: lambda, the average arrival rate, which in a stable system equals the throughput, in items per second (/s)
W: the average time each item spends inside the system, in seconds (s)
s: second
In words: the number of things inside equals how fast they arrive multiplied by how long each one stays.
```

It holds regardless of arrival distribution, and applies to a single thread pool, a whole service or a coffee shop.

**Example 1: sizing a thread pool.** A service handles 2,000 req/s, and each request spends 50 ms in the service (much of it waiting on the database):

```formula
L = λ × W
L = 2,000 /s × 0.050 s = 100
where
L: the average number of requests in the service at once
λ: lambda, the arrival rate, 2,000 requests per second (/s)
W: the time each request spends in the service, 50 ms = 0.050 s
s: second
In words: 2,000 requests arriving every second, each staying a twentieth of a second, means about 100 inside at any moment.
```

With one thread per request, you need at least ~100 threads (plus headroom).

**Example 2: database connections.** 5,000 queries/s at 4 ms each:

```formula
L = 5,000 /s × 0.004 s = 20
where
L: the average number of database connections busy at once
s: second; 4 ms = 0.004 s is how long each query holds a connection
In words: 5,000 queries a second, each holding a connection for 4 ms, keep about 20 connections busy.
```

A pool of 30–40 is a starting hypothesis, not a guarantee: burstiness, latency tails and database capacity determine the necessary headroom. A pool of 500 per app instance across 50 instances permits 25,000 connections and can impose substantial overhead; validate the total against database capacity rather than assuming more connections help.

**Example 3: what happens when latency rises.** The database slows from 4 ms to 40 ms while traffic stays at 5,000/s:

```formula
L = 5,000 /s × 0.040 s = 200
where
L: the average number of database connections needed at once
s: second; 40 ms = 0.040 s is the new time each query holds a connection
In words: the same traffic held ten times as long needs ten times as many connections.
```

The pool of 40 is exhausted; requests queue, latency rises further, and the problem cascades. Little's law explains why a slow dependency causes thread or connection-pool exhaustion upstream, and why timeouts and bulkheads (reliability module) matter.

## Scaling the different tiers

| Tier | Typical scaling approach |
|---|---|
| Static content | CDN |
| Stateless app | Horizontal + autoscaling |
| Read-heavy data | Cache + read replicas |
| Write-heavy data | Partition (shard) |
| Async work | Queue + worker pool |

Each technique gets its own lesson later. The pattern is consistent: find the bottleneck, apply the technique for that tier, then find the next bottleneck.

## Key takeaways
- Scalability means handling more load by adding resources, with roughly proportional cost; always specify which dimension of load.
- Vertical scaling is simple and surprisingly powerful but has a ceiling and is a single point of failure; horizontal scaling is near-unlimited but adds distributed-systems complexity.
- Stateless services scale trivially; push state into a few dedicated stateful systems and beware hidden state.
- Amdahl's law: the serial fraction caps speed-up at 1 divided by that fraction (a 5% serial part caps it at 20x), so find and remove serial bottlenecks.
- The USL adds coherence costs: a throughput curve that flattens means contention; one that falls means coordination overhead.
- Little's law (items inside = arrival rate × time inside) links concurrency, throughput and latency; use it to size pools and to predict pool exhaustion when latency rises.

## Further reading
- [Scalability (Wikipedia)](https://en.wikipedia.org/wiki/Scalability)
- [Amdahl's law (Wikipedia)](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Little's law (Wikipedia)](https://en.wikipedia.org/wiki/Little%27s_law)
- [Little's Law (Marc Brooker)](https://brooker.co.za/blog/2018/06/20/littles-law.html)
- [Neil J. Gunther and the Universal Scalability Law (Wikipedia)](https://en.wikipedia.org/wiki/Neil_J._Gunther)
- [The Twelve-Factor App: Processes](https://12factor.net/processes)
