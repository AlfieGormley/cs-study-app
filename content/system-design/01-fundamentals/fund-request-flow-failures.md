---
id: fund-request-flow-failures
title: Walk a request and challenge its failure modes
level: basic
minutes: 4
summary: Build a simple architecture, trace the critical path, and use cache failure and ticket inventory to expose hidden risks.
sourceLesson: fund-approach
---

Once the requirements and scale are clear, start with the simplest architecture that meets them. Trace a real request, then ask what happens when a component disappears or becomes slow.

## A repeatable approach

Most practitioners use some variant of this sequence:

```
1. Clarify requirements
   functional / non-functional / constraints
2. Estimate scale
   QPS, storage, bandwidth
3. Define the API and data model
4. High-level design
   boxes, arrows, request flow
5. Deep dive on the hard parts
   hot keys, consistency, failure
6. Identify bottlenecks and trade-offs
   what breaks first, what you'd change
```

### Step 4: the high-level design

Start with the simplest thing that meets the requirements, then evolve it.

```
 client
   |
   v
+--------+    +-----------+    +--------+
|  load  |--->|  app tier |--->|   DB   |
|balancer|    | stateless |    |primary |
+--------+    +-----------+    +--------+
                    |              |
                    v              v
                 +-----+      +--------+
                 |cache|      |replicas|
                 +-----+      +--------+
```

Walk a request through it: "A redirect hits the load balancer, goes to any app server, checks the cache, falls back to a read replica on a miss." Walking the flow catches missing pieces quickly.

### Step 5: deep dives

This is where the real design happens. Pick the parts that are hard *for this system*:

- How are short codes generated without collisions across many servers?
- What happens if the cache cluster fails?
- What's the hot-key story when one link goes viral?

The cache question deserves a quick calculation, because it decides whether the cache is an optimisation or critical infrastructure. The database only sees the reads the cache misses:

```formula
R_db = R_total × (1 − h)
h = 0.95: R_db = 0.05 × R_total
h = 0: R_db = R_total
where
R_db: the reads per second that reach the database, i.e. the cache misses
R_total: all reads per second arriving at the service
h: the cache hit rate, the fraction of reads the cache answers itself, from 0 (cache gone) to 1 (every read a hit); here 0.95, i.e. 95%
In words: the database carries only the share of reads the cache misses. At a 95% hit rate that is 5% of all reads; if the cache disappears the hit rate drops to 0 and the database carries every read, 1 / 0.05 = 20 times as many.
```

For example, at 100,000 reads/s the database normally sees 100,000 × 0.05 = 5,000 reads/s. With the cache gone it sees all 100,000 reads/s, a 20x jump. Can it survive that? The sum assumes every miss goes to the database and that clients don't add retries on top; in a real outage, retries make it worse.

Later modules cover the tools for these questions: caching, databases and partitioning, consistency and consensus, messaging, API design and reliability patterns.

## A worked mini-example

> [!example] "Design a ticket-booking system for concerts"
> **Functional:** browse events, hold seats for 10 minutes, pay, receive ticket.
>
> **Non-functional:** never sell the same seat twice (strong consistency on seat state); browse page p99 < 200 ms; survive a 50x traffic spike when a big tour goes on sale.
>
> **Constraints:** payments via an existing provider; 6 engineers; launch in 6 months.
>
> **Implications:** seat inventory needs transactions or conditional writes; the browse path can be heavily cached; the on-sale spike suggests a virtual waiting room or queue in front of checkout. Already the architecture is taking shape, and we haven't drawn a single box.

## Key takeaways
- Follow requirements, estimates, APIs, request flow, deep dives and explicit trade-offs.
- A cache at 95% hit rate hides a potential 20-fold database load increase when it fails.
- Ticket inventory needs concurrency-safe decisions; browse caching and a waiting room serve different goals.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
