---
id: db-scale-operational-budget
title: Scale triggers and operational cost
level: intermediate
minutes: 3
summary: Use measured bottlenecks, recovery objectives and team capability to evaluate distribution and database pricing.
sourceLesson: db-choosing
---

A candidate database must meet measured service objectives and be operable by the team. Capacity, recovery time, billing and engineer effort belong in the same decision.

## Scale

Be honest about it. A single well-run relational primary is a useful starting point; measure whether it meets this workload’s availability, throughput and recovery needs.

| Scale signal | Typical answer |
|---|---|
| Workload fits a measured single-node budget | One relational primary |
| Read-heavy beyond that | Replicas + cache |
| Writes beyond one node | Shard or distributed DB |
| Global low-latency writes | Multi-region store |

Scaling triggers worth acting on: cache misses cause unacceptable measured I/O or latency, write throughput nears the primary's limit even after tuning, or backups and restores take too long to meet recovery targets.

## Operational cost

The database you can *run well* beats the theoretically better one you can't.

- **Managed or self-hosted?** RDS, Aurora, Cloud SQL, DynamoDB, Atlas and Astra automate parts of patching, backups and failover; you still own configuration, recovery testing, access control and application behavior, at a price premium (and with some loss of control).
- **Team expertise.** Operating Cassandra well (repairs, compaction tuning, tombstones) is a real skill. Postgres knowledge is widespread.
- **Ecosystem.** Drivers, ORMs, migration tools, monitoring, backups, CDC connectors.
- **Cost model.** DynamoDB on-demand charges per request, and provisioned charges per capacity unit-hour, which can be cheaper for steady, predictable traffic; compare current regional rates, utilization and commitments rather than assuming a fixed saving. Aurora charges for instances plus storage, and either per I/O or a higher flat rate on its I/O-Optimized configuration. Self-hosted charges in engineer time.
- **Lock-in.** DynamoDB's API is proprietary; Postgres-compatible services let you move between providers.

> [!warning] Résumé-driven development
> Choosing a distributed database for a 50 GB dataset adds operational complexity. It can still be justified by regional availability, locality or throughput requirements; small size alone neither requires nor rules it out. Start simple, measure, and move when the numbers demand it.

## Apply the estimate to a retained sensor stream

Suppose two million sensors each send a reading every ten seconds: that is 200,000 readings per second, and at an assumed 100 bytes each, ninety days is about 155 TB before compression, indexes, replicas and overhead. Numbers like these change the question from "which product?" to "how do writes spread and how does old data leave?". A store keyed by sensor and a bounded time bucket, with expiry, is a candidate; benchmark ingestion, expiry and range queries rather than inferring an absolute single-node limit from the count.

## Key takeaways
- Tune and measure a primary before introducing distribution for a hypothetical bottleneck.
- Write saturation, working-set growth and recovery time are concrete scaling triggers.
- Compare current capacity prices and full operating costs, including recovery testing and engineer time.

## Further reading
- [DynamoDB: Capacity modes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/capacity-mode.html)
- [www.postgresql.org: performance tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [docs.aws.amazon.com: USER_WorkingWithAutomatedBackups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
