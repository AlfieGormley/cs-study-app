---
id: cs1-interview-workload-implications
title: Turn a workload estimate into design constraints
level: basic
minutes: 3
summary: Compute reads, writes and retained bytes separately.
sourceLesson: cs1-interview-framework
---

Use the daily-rate and decimal-byte conversions from the preceding unit. Here the objective is to explain what a concrete workload implies, rather than stopping after the arithmetic.

### A worked estimate

Take a service with 100M (100 million) daily active users (DAU) who each make 10 reads and 1 write per day. First the rates:

```formula
writes = 100M × 1 / (10^5 s) = 1,000/s
reads = 100M × 10 / (10^5 s) = 10,000/s
peak writes = 1,000/s × 3 = 3,000/s
peak reads = 10,000/s × 3 = 30,000/s
where
writes, reads: average write and read requests per second
peak writes, peak reads: the same rates at the busiest time, using an assumed peak factor of 3
M: million (10^6); 100M is 100,000,000 users
10^5: 100,000, the rounded number of seconds in a day
s: seconds; /s means per second
In words: 100 million users doing one write a day is about a thousand writes a second, ten times that for reads, and three times both at peak.
```

(Dividing by the exact 86,400 gives about 1,160 writes/s and 11,600 reads/s; the shortcut is close enough.)

Then storage, assuming each write stores about 1 KB:

```formula
daily = 100M × 1 KB = 100 GB
yearly = 100 GB × 365 ≈ 36 TB
where
daily, yearly: new data stored per day and per year, before replication
M: million (10^6)
KB: kilobyte, 1,000 bytes
GB: gigabyte, 10^9 bytes
TB: terabyte, 10^12 bytes (1,000 GB)
≈: approximately equal to (36.5 rounded down)
In words: 100 million 1 KB writes a day is 100 GB a day, which adds up to about 36 TB a year.
```

Now you know: reads dominate 10:1 (cache them), 3k writes/s is a target to test against the chosen primary (and a partitioning strategy is useful if tests reveal a limit), and storage grows by tens of terabytes a year.

Say what the numbers *imply*. "36 TB a year, nearly 200 TB over five years before replication, requires a storage, backup and recovery plan; I will evaluate partitioning, tiering and sharding against those constraints" is worth far more than the arithmetic itself.

## Make the assumption visible

The 100-million-user example is hypothetical. The peak multiplier and record size are inputs to test, rather than facts about an existing deployment. A small change in record size can dominate a long retention period: indexes and replication are additional to the raw total.

Treat the estimate as a decision record. Name the query that is expensive, the bytes that need retaining, and the failure or latency target a candidate store must meet. Benchmark the proposed workload before concluding that one machine or a shard is enough. This also explains why adding sharding merely because a daily count sounds large is premature.

## Key takeaways

- Compute reads, writes and retained bytes separately.
- A read-heavy ratio suggests caching; it does not establish database capacity.
- Include retention, replication, backups and recovery in the storage plan.

## Further reading

- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
