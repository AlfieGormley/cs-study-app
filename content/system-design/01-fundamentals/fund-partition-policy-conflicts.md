---
id: fund-partition-policy-conflicts
title: Choose a partition policy and plan reconciliation
level: advanced
minutes: 3
summary: Separate CAP availability from operational uptime, and match refusal or conflict resolution to each data type.
sourceLesson: fund-cap-pacelc
---

The CAP proof identifies a constraint; the product still needs a policy. Decide which operations may continue during isolation and what the application must do when connectivity returns.

## CAP availability and operational uptime

CAP availability is extreme: *every* non-failing node must respond successfully, even a node isolated on the minority side of a partition.

Real systems usually mean something weaker by "highly available": most requests succeed most of the time. Systems using **majority quorums** (Raft in etcd, Paxos in Spanner, the similar Zab protocol in ZooKeeper) commonly refuse writes on the minority side during a partition. That consistency-oriented write policy does not establish that every read API is linearisable; ZooKeeper reads, covered below, may be stale. Yet such systems routinely achieve very high availability, because:

- Partitions are relatively rare.
- Clients on the minority side can often fail over to the majority side.

Google Spanner offers a 99.999% monthly uptime commitment for multi-region configurations under its SLA measurement and credit conditions. This can coexist with refusing operations that cannot safely reach the required replicas; the SLA is not a CAP-availability promise.

## Guarantees matter more than labels

Martin Kleppmann's essay "Please stop calling databases CP or AP" makes the case well. Most real systems are **neither** strictly:

- Many offer **tunable** consistency per request. Cassandra lets you pick `ONE`, `QUORUM` or `ALL`; DynamoDB offers eventually consistent or strongly consistent reads.
- Many aren't linearisable even without partitions (e.g. asynchronous replication with reads from replicas), so they don't satisfy CAP's C anyway.
- Many aren't CAP-available either (e.g. a leader-based system where nodes refuse writes when they can't see the leader).

A system that is neither linearisable nor CAP-available is just... a system with other trade-offs. Describe its *actual* guarantees instead: "reads may be up to ~1 s stale", "writes are rejected on the minority side".

## Using this in a design

1. **Decide per data type, not per system.** A bank's balance needs strong consistency; its "recently viewed" list doesn't.
2. **Ask what happens on the minority side of a partition.** Refuse writes? Accept and reconcile later? Serve stale reads with a warning? Brewer's own example is an ATM: during a partition it can keep dispensing cash up to a small limit, accepting a bounded risk and reconciling (and charging overdraft fees) afterwards.
3. **If you choose availability, plan for conflicts.** Last-write-wins (loses data silently), version vectors with application merge, or CRDTs. Amazon's original Dynamo merged conflicting shopping carts, occasionally resurrecting deleted items.
4. **If you choose consistency, plan for unavailability.** Clients need retries, timeouts and clear errors.
5. **Quantify the latency cost.** For an exercise, assume a same-zone quorum takes 1 ms and a cross-region quorum tens to hundreds of milliseconds. Real quorum latency depends on replica placement, protocol and workload; measure it.

The distributed consistency and consensus module covers linearisability, quorums, Raft and conflict resolution in depth.

## Key takeaways
- A majority-quorum system may have high measured uptime while refusing requests on a minority side.
- Choosing to accept partitioned updates requires an application-appropriate conflict-resolution policy.
- Choosing consistency requires client-visible errors, timeouts and recovery behaviour.
- Choose per data type and quantify the latency and business risk of the policy.

## Further reading
- [CAP Twelve Years Later (Eric Brewer)](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Eventually Consistent (Werner Vogels)](https://www.allthingsdistributed.com/2008/12/eventually_consistent.html)
- [Dynamo: Amazon’s Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Spanner availability SLA](https://cloud.google.com/spanner/sla)
