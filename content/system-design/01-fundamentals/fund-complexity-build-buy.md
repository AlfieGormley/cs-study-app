---
id: fund-complexity-build-buy
title: Choose manageable complexity and record the decision
level: advanced
minutes: 3
summary: Compare build with buy, distinguish reversible choices, and communicate the operating cost and assumptions.
sourceLesson: fund-tradeoffs
---

A design must fit the people who operate it. Compare the value of a component with the complexity it introduces, decide which work the team should own, and leave a record future engineers can reassess.

## Complexity

Complexity is the cost that's easiest to underestimate. Every component adds:

- Things to deploy, upgrade, monitor and secure.
- New failure modes and interactions between them.
- Knowledge the team must hold (and lose when people leave).

Questions to ask:

- Could a **simpler** design meet the requirements? A Postgres table with `SELECT ... FOR UPDATE SKIP LOCKED` is a perfectly good job queue at moderate scale.
- Is the complexity **essential** (required by the problem) or **accidental** (introduced by our choices)?
- Is the complexity **reversible**? Prefer decisions you can undo cheaply. Amazon calls these "two-way doors"; spend careful thought on the "one-way doors" (data models, public APIs, core storage).

Microservices are the canonical example. They buy independent deployment and team autonomy, at the price of distributed failure modes, network latency, eventual consistency between services and much more operational work. Martin Fowler's advice is to start with a monolith unless you have a strong reason not to.

## Build vs buy

| Factor | Favours build | Favours buy/managed |
|---|---|---|
| Core differentiator? | Yes | No |
| Team expertise | Deep | Thin |
| Time to market | Flexible | Urgent |
| Scale/cost at volume | Huge | Moderate |
| Control needed | High | Standard |

- **Buy (or use managed)** for undifferentiated heavy lifting: databases, queues, auth, email, payments, observability. Running your own Kafka or Elasticsearch cluster needs real expertise.
- **Build** when it's your core competitive advantage, when vendors can't meet a hard requirement, or when scale makes vendor pricing untenable. Dropbox moved most of its storage off S3 onto its own infrastructure ("Magic Pocket") only once it stored hundreds of petabytes.
- Watch for **lock-in**, but don't over-pay for portability you'll never use. Abstracting every cloud service "in case we migrate" is itself a cost.

## Other recurring trade-offs

- **Normalisation vs denormalisation**: storage and write simplicity vs read speed. (Databases module.)
- **Push vs pull**: precomputing feeds on write (fan-out on write) vs assembling on read. (Case studies.)
- **Synchronous vs asynchronous**: simple and immediately consistent vs decoupled and resilient. (Messaging module.)
- **Generality vs specialisation**: one flexible store vs purpose-built stores for search, analytics and caching.
- **Freshness vs cost**: cache TTLs, CDN expiry. (Caching module.)

## Communicating trade-offs

In design reviews and interviews, it helps to:

- **Present options, not just a conclusion.** "We considered A and B; we chose B because..."
- **Quantify.** "Synchronous cross-region replication adds ~80 ms per write; our p99 budget is 200 ms."
- **Write it down.** An Architecture Decision Record (context, decision, consequences) lets future engineers understand *why*, and see when the assumptions no longer hold.

## Key takeaways
- Every additional component brings deployment work, knowledge and interacting failure modes.
- Spend careful effort on hard-to-reverse data and API decisions; test simpler reversible choices cheaply.
- Use managed services for work that does not differentiate the product when the team and costs favour it.
- Record options, consequences and revisit conditions in an Architecture Decision Record.

## Further reading
- [Microservice Trade-Offs (Martin Fowler)](https://martinfowler.com/articles/microservice-trade-offs.html)
- [MonolithFirst (Martin Fowler)](https://martinfowler.com/bliki/MonolithFirst.html)
- [Magic Pocket (Dropbox)](https://dropbox.tech/infrastructure/magic-pocket-infrastructure)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
