---
id: fund-parallel-scaling-limits
title: Find the serial and coordination limits of scaling
level: intermediate
minutes: 4
summary: Apply Amdahl’s law and node-pair growth to explain why more workers can stop helping or reduce throughput.
sourceLesson: fund-scalability
---

Once a workload can use several workers, the next question is how much speed-up they can provide. Fixed serial work and coordination overhead place different limits on that benefit.

## Amdahl's law: the limit of parallelism

Some part of almost every job can only be done one step at a time (it is **serial**); the rest can be split across workers (it is **parallel**). Gene Amdahl pointed out in 1967 that the serial part limits how much faster extra workers can make the job. Measure the job's time on one worker as 1; the serial share still takes the same time, while the parallel share is divided between the workers:

```formula reference
S(N) = 1 / ((1 − p) + p / N)
S_max = 1 / (1 − p)
where
S(N): the speed-up with N workers: how many times faster the job runs than on one worker
N: the number of workers (cores, machines) sharing the parallel part
p: the parallel fraction, the share of the one-worker running time that can be split between workers, from 0 to 1; the finite ceiling below assumes a nonzero serial share, so p is less than 1
1 − p: the serial fraction, the share that must run on one worker whatever happens
S_max: the limit of S(N) as N grows without bound (infinitely many workers): the parallel term p / N shrinks to 0
In words: extra workers shorten only the work that can run in parallel. The serial work remains, so it eventually dominates and limits the benefit of adding workers.
```

For example, if 5% of the original job is serial, even unlimited workers cannot make the fixed job more than twenty times faster. This assumes the parallel part splits perfectly with no coordination overhead; real overhead can reduce the benefit further.

| Parallel share | Max speed-up |
|---|---|
| 50% | 2x |
| 90% | 10x |
| 95% | 20x |
| 99% | 100x |

With 95% parallel, the ideal speed-up approaches a twentyfold limit as workers increase. For an entirely parallel job, this ideal model has no serial floor; practical communication and resource limits still apply.

In system design, a shared bottleneck may play a similar limiting role. These components are not necessarily single-threaded, but each has finite capacity:

- A single primary database that handles all writes.
- A global lock or a single-threaded sequencer.
- A single coordinator service.

Amdahl tells you that adding app servers won't help once you're bottlenecked on one of these. You must remove or partition the serial component.

> [!note] Universal Scalability Law
> Real systems often do worse than Amdahl, because nodes must coordinate (cache coherence, cross-node chatter). Neil Gunther's USL models two costs: **contention** (queueing for a shared resource, which is Amdahl's serial part) and **coherence** (nodes keeping each other up to date). Coherence cost grows roughly with the number of node *pairs*, which grows much faster than the number of nodes (illustrated below), so it can make throughput *fall* as you add nodes.
>
> The shapes are diagnostic. A curve that rises then **flattens** points to contention: find the shared bottleneck. A curve that rises then **falls** points to coherence: look for all-to-all chatter, global locks or broadcast cache invalidation.

With eight nodes there are 28 distinct pairs; with sixteen there are 120. Doubling the nodes creates more than four times as many possible pairwise relationships in this example. If each node talks to every other on each update, coordination can grow faster than useful work.

Gustafson's law gives the optimistic counterpart: as you add machines you usually also grow the *problem* (more users, more data), so the parallel portion grows and scaling stays useful.

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
- For a fixed job, the serial fraction caps speed-up even with unlimited workers.
- Coordination between node pairs can grow much faster than the number of nodes.
- Treat curve shapes as clues, then measure the bottleneck and scale the tier responsible.

## Further reading
- [Amdahl’s law](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Neil Gunther and the Universal Scalability Law](https://en.wikipedia.org/wiki/Neil_J._Gunther)
- [Little’s Law (Marc Brooker)](https://brooker.co.za/blog/2018/06/20/littles-law.html)
- [Gunther: quantifying scalability](https://www.perfdynamics.com/Manifesto/USLscalability.pdf)
