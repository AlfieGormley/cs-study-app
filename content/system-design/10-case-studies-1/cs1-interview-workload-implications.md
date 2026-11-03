---
id: cs1-interview-workload-implications
title: Turn a workload estimate into design constraints
level: basic
minutes: 3
summary: Compute reads, writes and retained bytes separately.
sourceLesson: cs1-interview-framework
---

A useful workload estimate changes a decision. Separate reads, writes and retained data because each stresses a different part of the system.

## Interpret a hypothetical workload

Suppose users make ten reads for each write, and the retained payload grows by tens of terabytes per year. These are illustrative inputs, not measurements of an existing company.

- **Reads:** repeated access to the same cacheable data may benefit from a cache. A read-heavy ratio alone does not establish reuse or acceptable staleness.
- **Writes:** benchmark the actual transaction, indexes, contention and durability policy. Introduce partitioning or sharding when a measured constraint justifies it.
- **Retention:** budget for the full retained dataset, indexes, replicas, backups and temporary migration space. Recovery time can become a constraint before storage space is exhausted.

## Challenge the assumptions

A larger record or longer retention period increases retained bytes even if request rate stays unchanged. A highly skewed workload can overload one key while other machines are idle. Adding nodes only helps if the work can be distributed across them.

Treat the estimate as a decision record: identify the expensive queries, the data that must remain available and the recovery target. Compare keeping everything in one store with time partitioning, moving cold data to cheaper storage, or sharding. Each choice changes operations and query behaviour.

## Key takeaways

- Assess reads, writes and retained bytes separately.
- A read-heavy ratio suggests investigating caching; it does not prove useful reuse.
- Include growth, backups and recovery before deciding how to distribute storage.

## Further reading

- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
