---
id: arch-multi-region
title: Multi-region and geo-distributed architecture
level: advanced
minutes: 16
summary: Why and how systems span several regions, the trade-offs between active-passive and active-active, data residency constraints, handling write conflicts, and limiting blast radius with cell-based architecture.
---

A cloud region may offer several availability zones, each with separate infrastructure and possibly multiple data centres. A correctly configured multi-AZ workload can tolerate specified zone failures, but a region label alone does not guarantee application availability. So why go **multi-region**?

- **Disaster recovery**: whole regions do fail, or partially fail in ways that look total (control-plane outages, bad deploys of regional services, major network events).
- **Latency**: long paths impose propagation delay. A hypothetical 17,000 km fibre path at 200 km/ms takes 85 ms one way before routing and equipment overhead; actual routes and measured RTTs differ. Serving Australian users from Australia matters.
- **Data residency**: laws and contracts may require data about EU residents, or a particular government's citizens, to stay in specific places.

It's also expensive and hard. Extra regions add infrastructure and operating costs and, more importantly, forces you to confront **the speed of light in your data layer**.

## The fundamental trade-off

Synchronous acknowledgment latency depends on required replicas, distance, storage and protocol. Benchmark the chosen deployment.

> [!note] Evidence gap
> Generic cross-AZ/region latency and recovery-time estimates are omitted because no measured deployment establishes them. Numeric quiz examples state hypothetical inputs. That gives you a choice for each piece of data:

- **Synchronous cross-region replication**: can protect acknowledged commits from loss of one region when they are durably retained in a surviving region and failover selects the correct replica; this can meet a zero-loss objective for that failure model. Each required remote acknowledgment adds latency, and writes stop if the required remote acknowledgements or quorum become unreachable; a three-region quorum can continue after losing one region.
- **Asynchronous replication**: fast local writes, but a failure can lose acknowledged writes not yet durably replicated. Observed lag does not by itself guarantee a worst-case recovery point.

This is CAP and PACELC in practice: under a partition you choose consistency or availability, and even without one you choose latency or consistency.

Two numbers frame every DR design:

- **RPO** (recovery point objective): how much data you can afford to lose, measured in time.
- **RTO** (recovery time objective): how long you can be down.

## Active-passive

One region (primary) serves all traffic; another (standby) receives replicated data and takes over if the primary fails.

```
        users
          |
     [ DNS / GLB ]
       |       :  (failover)
       v       v
  [Region A]  [Region B]
   active      standby
     DB ==async==> DB replica
```

Variants by how "warm" the standby is (AWS names these in its DR guidance):

| Strategy | Standby | Recovery work |
|---|---|---|
| Backup & restore | Backups | Restore data and provision services |
| Pilot light | Data and core infrastructure | Start missing services and scale |
| Warm standby | Reduced working deployment | Redirect traffic and add capacity |
| Hot standby | Provisioned working deployment | Promote/fence writers and redirect traffic |

Pilot light can't serve requests until you switch servers on and scale up; warm standby can take traffic immediately at reduced capacity and only needs to scale up. Hot standby is provisioned for full production load, so it doesn't depend on autoscaling working during a disaster, which AWS calls *static stability*.

Pros: simpler write ownership, if failover fences the old primary so only one writer remains authoritative. Cons: the standby is paid for but idle, users far from the primary get high latency, and **failover is a rarely exercised, risky operation**. Many outages get worse because failover itself fails: stale runbooks, DNS TTLs that don't expire as expected, untested capacity in the standby.

> [!warning] Untested failover isn't failover
> Exercise failover and restore procedures on a schedule appropriate to the system, including controlled production traffic shifts where justified. Verify fencing, recovery point, routing, capacity and rollback.

> [!note] Replication isn't backup
> Cross-region replication faithfully copies mistakes too. Logical deletions and corrupting writes can propagate to replicas. Keep tested backups and retained logs, with appropriately isolated access. The latest recoverable good state depends on available backups, logs and the incident; an RPO is a target, not simply the age of one backup.

## Active-active

Every region serves live traffic. Users are routed to the nearest healthy region (latency-based DNS, anycast, or a global load balancer).

```
  EU users         US users
     |                |
 [Region EU] <----> [Region US]
  reads +    async    reads +
  writes   replicate  writes
```

Pros: local serving can reduce latency and each region exercises a production path. Failure routing, data promotion and spare-capacity behavior still need separate tests; active-active does not exercise every failover scenario.

Cons: if both regions accept writes to the **same data**, you must handle **conflicts**. And each region needs spare capacity to absorb the other's traffic: with two regions, the simple equal-capacity, equally loaded linear model requires each to use at most 50% of available capacity before loss of one. Real designs need margin and must account for state, retries, caches and resource-specific bottlenecks.

### Avoiding conflicts: partition the writes

The simplest active-active design gives each piece of data a **home region**:

- A user's account lives in the region where they signed up; all writes for that user go there.
- Other regions can serve **reads** from asynchronous replicas, and forward writes to the home region.
- One authoritative writer avoids concurrent cross-region ownership if enforced through failover fencing. Local transactions still need concurrency control, and multi-record operations can require coordination.

This is often called *geo-partitioning*. CockroachDB, Spanner and DynamoDB-based designs commonly use it, and it lines up neatly with data residency.

### When you must accept multi-region writes: conflict handling

If two regions can write the same record concurrently (DynamoDB global tables, Cassandra multi-DC, CouchDB, multi-primary MySQL), concurrent writes will collide. Options:

1. **Last-writer-wins (LWW)**: keep the write with the highest timestamp. Simple, and what DynamoDB global tables do in their default, eventually consistent mode, but it **silently discards** the other write, and clock skew can make the "wrong" one win. (Since 2025 DynamoDB also offers a multi-Region *strongly* consistent mode for global tables, which avoids conflicts by paying cross-region latency on writes.)
2. **Merge by data type**: use **CRDTs** (conflict-free replicated data types) that converge under their required delivery and merge assumptions, including eventual exchange of updates: counters (each region increments its own slot; the total is the sum), sets with add/remove semantics, registers with defined rules. Riak and Redis Enterprise's active-active mode use CRDTs.
3. **Application-level resolution**: keep both versions (siblings) and let the application or the user merge them, as with conflicting edits in a document.
4. **Avoid it for invariants**: anything with a hard constraint (account balance must not go negative; one seat sold once) usually uses a single writer or a consensus-based store (Spanner, CockroachDB). Some bounded invariants can instead use escrow: preallocate disjoint spending or stock rights to regions, and reject locally when rights run out. Transferring rights then requires coordination.

> [!example] Shopping basket vs bank balance
> A basket can use a CRDT with chosen add/remove semantics, but quantities, checkout, deletion and inventory constraints still need explicit product rules. Convergence alone does not bound every bad outcome. An ordinary mergeable balance counter cannot safely let both regions independently approve £100 against the same £150 balance. Escrow can partition spending rights, but neither region may spend beyond its allocation. Route balance updates to the account's fenced home region, or use a strongly consistent store, and atomically validate and apply each debit.

## Data residency

Consider a hypothetical tenant whose contract explicitly requires EU-only storage and processing. The following is an architecture exercise for that stated requirement.

> [!note] Content gap
> Jurisdiction-specific legal requirements are not assessed here: no applicable contract, sector or legal analysis was supplied. This lesson does not assert that every EU customer has an EU-only obligation.

- **Pin data to a region by tenant or user**: EU customers' records live and are processed in EU regions, and are not replicated to the US.
- **Separate global from local data**: product catalogues and configuration can be global; personal data stays local. A global directory can map opaque tenant identifiers to home regions, but identifiers and routing metadata may themselves be personal data if they can be linked to a person; minimise and govern that data too.
- **Watch the side channels**: backups, logs, analytics pipelines, search indexes, caches and support tools all copy data. Residency applies to every copy.
- **Disaster recovery inside the boundary**: fail over from Frankfurt to another EU region, not to Virginia.

## Cell-based architecture

Multi-region protects you from a *region* failing. But many outages are caused by **you**: a bad deploy, a poison-pill request, a runaway tenant, a configuration change. Shared dependencies can let such failures affect many customers.

A **cell-based architecture** divides the system into many independent, identical copies called **cells**, each serving a subset of customers, with no shared state between cells.

```
         [ thin cell router ]
        /    |    |    |     \
   [cell1][cell2][cell3]...[cellN]
   each: own app tier, DB, cache, queues
   customers mapped to one cell
```

- **Blast radius**: a cell-local failure can be contained to that cell if shared dependencies remain healthy. With 20 equally populated cells, one cell holds 5% of customers.
- **Staged deploys**: roll out to one cell, watch, then expand in waves.
- **Known scaling limits**: each cell has a fixed maximum size that has been load tested. Growth means adding cells, not scaling one system into unknown territory.
- **Routing layer**: a thin, extremely simple router (often a lookup of customer → cell) is a shared dependency to keep minimal and robust; audit other shared services and control-plane dependencies too.

AWS uses cells extensively (it publishes guidance on the pattern), Slack migrated to a cellular architecture aligned with availability zones after zone-level incidents, and Azure calls the pattern **Deployment Stamps**. A related AWS technique, **shuffle sharding**, assigns each customer to a random combination of a few nodes, so that one customer's poison traffic overlaps fully with very few others.

Cells and regions combine: each region contains several cells; a customer's cell lives in their home region; DR replicates each cell to a paired region.

## Putting it together

A realistic design for a global SaaS:

1. Users are assigned a **home region** (by residency or proximity) and a **cell** within it.
2. A global directory and router send requests to the right cell, wherever the user connects.
3. Each cell replicates asynchronously to a standby in a paired region inside the same jurisdiction (define objectives and verify recovery point and duration with drills).
4. Truly global data (catalogue, feature flags) is replicated everywhere, read-mostly.
5. Invariant-critical operations stay single-writer; commutative data (likes, presence, baskets) can be multi-writer with CRDTs.

## Key takeaways
- Go multi-region for disaster recovery, latency and residency, and expect the speed of light to dominate your data design.
- Active-passive is simpler but leaves capacity idle and makes failover a risky, rarely exercised event; define RPO and RTO and test failover regularly.
- Active-active exercises normal serving in each region; failover still needs testing. Home-region ownership can avoid cross-region write conflicts if fencing is enforced.
- When multi-writer is unavoidable, choose LWW, CRDTs or application merges deliberately, and keep invariant-critical data single-writer or strongly consistent.
- Data residency applies to every copy: backups, logs, caches and analytics included.
- Cell-based architecture limits the blast radius of failures you cause yourself by splitting the system into independent, size-limited cells.

## Further reading
- [AWS: Disaster recovery options in the cloud](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [AWS: What is a cell-based architecture?](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html)
- [AWS Builders' Library: Workload isolation using shuffle-sharding](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/)
- [Slack: Slack's migration to a cellular architecture](https://slack.engineering/slacks-migration-to-a-cellular-architecture/)
- [Azure Architecture Center: Deployment Stamps pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/deployment-stamp)
- [Azure Architecture Center: Geode pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/geodes)
- [AWS: DynamoDB global tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html)
- [Wikipedia: Conflict-free replicated data type](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
