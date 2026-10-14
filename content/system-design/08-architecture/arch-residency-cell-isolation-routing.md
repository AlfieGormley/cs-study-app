---
id: arch-residency-cell-isolation-routing
title: Placing data inside isolated cells
level: advanced
minutes: 5
summary: Apply an explicit residency requirement to every copy and contain local operational failures with cells.
sourceLesson: arch-multi-region
---

Regional replication and conflict rules do not contain every bad deploy or runaway tenant. Combine home-region placement with smaller independent stacks and audit every data-copy path.

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

- **Blast radius**: a cell-local failure can be contained to that cell if shared dependencies remain healthy. With 20 equally populated cells, one cell holds 1/20 = 5% of customers.
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

### Why shuffled assignments reduce full overlap

With fixed groups of four workers, a customer's traffic that breaks all four removes every worker for its whole group. Shuffle sharding instead assigns customers different four-worker combinations drawn from the larger fleet. Another customer loses every assigned worker only when its combination fully overlaps the failed one; partial overlaps can leave a healthy retry route. The combination calculation in the question assumes independent uniform assignments. It does not guarantee that every partially overlapping customer has spare capacity or that shared dependencies survive.

## Key takeaways
- A stated residency boundary covers backups, logs, analytics, search, caches and support paths as well as the primary.
- Cells isolate full serving stacks and bound tested scale; shared routers and control planes still require scrutiny.
- Staged cell deployment and tenant isolation reduce impact only when failures stay within the intended boundary.
- Shuffle sharding reduces full overlap between assigned worker sets, assuming healthy retry alternatives and sufficient capacity.

## Further reading
- [AWS: What is a cell-based architecture?](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html)
- [AWS Builders' Library: Workload isolation using shuffle-sharding](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/)
- [Slack: Slack's migration to a cellular architecture](https://slack.engineering/slacks-migration-to-a-cellular-architecture/)
- [Azure Architecture Center: Deployment Stamps pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/deployment-stamp)
