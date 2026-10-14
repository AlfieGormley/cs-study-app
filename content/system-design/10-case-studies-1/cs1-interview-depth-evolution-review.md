---
id: cs1-interview-depth-evolution-review
title: Use deep dives to explain failure and evolution
level: basic
minutes: 4
summary: Choose the hard parts specific to this design and compare alternatives.
sourceLesson: cs1-interview-framework
---

## Step 6: Deep dives

This is where you earn the senior rating. Pick the two or three hardest parts of *this* problem and go deep:

- URL shortener: unique ID generation without coordination.
- Chat: delivering to a user connected to a different server.
- News feed: the celebrity with 100M followers.

Often the interviewer will steer you here. If they don't, choose yourself: "The interesting part is fan-out; shall I go deep on that?"

For each deep dive, show **options and trade-offs**, then choose. "We could hash the URL, use a counter, or use Snowflake IDs. Hashing needs collision handling; a counter needs coordination; Snowflake IDs need clock discipline. I'll use a counter with range allocation because..."

Also cover failure: what happens when this node dies, this region goes dark, this queue backs up? Senior engineers think about failure modes by reflex.

A useful checklist of probes that come up in almost every design, so you can raise them before you're asked:

- **Hot keys and skew**: one celebrity, one viral link, one huge group chat.
- **Retries and duplicates**: what is idempotent, and where is the dedup key?
- **Data consistency**: which reads can be stale, and for how long?
- **Backpressure**: what happens when a downstream dependency is slow, and does the queue grow without bound?
- **Fail-open or fail-closed**: when a dependency is down, do you allow the request or reject it?
- **Multi-region**: where do writes go, and what does a user see after a regional failover?

## Step 7: Wrap up and evolve

Spend the last few minutes on:

- **Bottlenecks**: what breaks first as load grows?
- **10x scale**: what would you change? (Shard further, add regions, move to async processing.)
- **Operational concerns**: monitoring, alerting, deployment, data migration.
- **Cost**: at staff level, say which component dominates the bill (often storage or egress) and one way to cut it.

Finish with a one-sentence summary of the design and its key trade-off. It leaves the interviewer with a clear picture to write up.

## A practice review checklist

Use these dimensions as a practice checklist; they are not asserted to be the scorecard of most companies:

1. **Problem navigation**: did you clarify scope, or charge off in a random direction?
2. **Solution design**: does the design actually work end to end and meet the requirements?
3. **Technical depth**: can you go deep on at least a couple of components (database internals, consistency, caching behaviour)?
4. **Trade-offs**: do you articulate alternatives and *why* you chose one?
5. **Communication**: can the interviewer follow your reasoning? Do you respond well to hints?

Seniority changes the bar. A mid-level candidate is expected to produce a working design with some guidance. A senior candidate drives the conversation, identifies the hard parts unprompted, and discusses failure modes. A staff candidate also talks about evolution, operability, cost and organisational trade-offs.

## Common mistakes

- **Jumping to the solution.** Drawing Kafka in minute two, before you know whether the system does 10 writes per second or 10 million.
- **Over-engineering.** Microservices, three caches and a service mesh for a system that fits on one database. Scale the design to the numbers.
- **Buzzword architecture.** Naming technologies without saying what they do for this problem. "I'll use Cassandra" means nothing without "because the access pattern is a partitioned time-ordered range scan and we need high write throughput".
- **Ignoring the interviewer.** If they ask "what about hot keys?" it's a hint, not small talk.
- **Silent thinking.** The interviewer can only score what they hear. Think out loud.
- **Not finishing.** A complete simple design beats a half-finished elaborate one. Get end to end first, then deepen.
- **Pretending.** If you don't know how something works, say so and reason from first principles. Bluffing is easy to spot.

> [!warning] Estimates are a tool, not a ritual
> Some candidates spend ten minutes on estimates and then never refer to them again. Only compute numbers that will change a decision, and then use them.

## Key takeaways

- Choose the hard parts specific to this design and compare alternatives.
- Probe hot keys, retries, consistency, backpressure and regional failure.
- Describe the first growth bottleneck, a safe migration, cost and observability.

## Further reading

- [Amazon: SDE interview preparation](https://amazon.jobs/content/en/how-we-hire/sde-ii-interview-prep)
- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
