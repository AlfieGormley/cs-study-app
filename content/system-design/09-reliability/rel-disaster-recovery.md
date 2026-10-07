---
id: rel-disaster-recovery
title: Disaster recovery and chaos engineering
level: intermediate
minutes: 12
summary: Set RPO and RTO targets, choose between backup-restore, pilot light, warm standby and active-active, and prove it all works with drills and chaos experiments.
---

High availability handles the failures you expect every week: a host dies, a zone blips. **Disaster recovery (DR)** handles the rare, large ones: a region goes dark, a ransomware attack encrypts your database, an engineer runs `DROP TABLE` in production, or a bug silently corrupts data for a week.

DR planning starts with two numbers and ends with a drill.

## RPO and RTO

```
        disaster
           │
 ──────────┼──────────────────▶ time
   ◀─RPO──▶│◀──────RTO──────▶│
 last good │                 │ service
 copy      │                 │ restored
```

- **Recovery Point Objective (RPO)**: the maximum acceptable *data loss*, measured as time. RPO of 15 minutes means you can lose at most the last 15 minutes of writes.
- **Recovery Time Objective (RTO)**: the maximum acceptable *downtime*, from disaster to service restored.

These are business decisions, not technical ones. Ask "what does an hour of downtime cost?" and "what does losing an hour of orders cost?" Then compare against the cost of each DR strategy.

These are illustrative business targets, not industry defaults.

| Workload | Example RPO | Example RTO |
|---|---|---|
| Internal wiki | 24h | 1–2 days |
| E-commerce site | minutes | < 1 hour |
| Payments ledger | ~0 | minutes |

> [!note] RPO is driven by replication; RTO by automation
> RPO depends on how often data leaves the primary location (backup frequency, async replication lag). RTO depends on how much has to happen before you can serve: provisioning, restoring, DNS changes, and how many of those steps are manual.

## Backups: the foundation

Replication is not a backup. If someone deletes a table, replication normally propagates the deletion to replicas; timing and replay behavior vary. Backups protect against **logical** failures (bugs, mistakes, attacks) that replication copies.

Good backup practice:

- **Point-in-time recovery (PITR)**: periodic full snapshots plus continuous write-ahead log archiving. Postgres with WAL archiving, MySQL binlogs, and AWS RDS PITR can recover to supported points within the available, continuous backup/log history, up to the latest restorable point. Your RPO is set by how often log segments actually leave the server: RDS, for example, typically uploads logs every five minutes, so its latest restorable time is usually a few minutes behind.
- **3-2-1 rule**: 3 copies, on 2 different media or services, with 1 off-site.
- **Immutability**: enforced write-once retention (such as S3 Object Lock compliance mode) protects retained object versions from deletion, including by administrators. Governance mode can be bypassed by authorized users. Protect encryption keys too: immutable ciphertext is useless if its key is destroyed.
- **Separate account or project**: backups stored where the production credentials cannot reach.
- **Test restores regularly**. A backup that has never been restored is a hope, not a backup.

> [!warning] The restore you didn't test
> Google's SRE book chapter on data integrity makes the point bluntly: nobody really wants backups, they want restores. Automate restore tests and measure how long a full restore takes, because that time is your RTO floor for backup-based recovery.

### Restore time maths

Restore time often dominates RTO. Restoring 20 TB at an effective 500 MB/s takes:

```
20,000,000 MB / 500 MB/s
= 40,000 s ≈ 11.1 hours
```

Plus applicable log replay, validation and any rebuild work required by the backup format; physical database backups generally already include indexes. If the business wants a 1-hour RTO, a restore-from-backup strategy can't meet it.

## The four DR strategies

The AWS DR whitepaper describes a spectrum from cheap and slow to expensive and fast. The ranges below are illustrative planning categories, not guarantees: backup plus continuous log archiving can have a low RPO, while active-active asynchronous replication can still lose acknowledged writes.

```
Cost ▲
     │                   ● Active-active
     │             ● Warm standby
     │       ● Pilot light
     │ ● Backup & restore
     └──────────────────────────▶
       hours        mins    ~0
              RTO / RPO
```

### 1. Backup and restore

Back up data (and infrastructure as code) to another region. In a disaster, provision everything and restore.

- RPO: hours (backup interval). RTO: hours to a day.
- Cost: backup storage, copying, restore testing and recovery compute, with little continuously running application capacity.
- Fine for internal tools and batch systems.

### 2. Pilot light

The *core* data layer runs continuously in the DR region (e.g. a cross-region database replica), but application servers are off or scaled to zero. In a disaster, scale up the app tier and switch traffic.

- RPO: minutes (replication lag). RTO: tens of minutes.
- Cost: the replica plus minimal infrastructure.

### 3. Warm standby

A scaled-down but **fully functional** copy runs in the DR region and can take traffic immediately, at reduced capacity, while it scales up.

- RPO: seconds to minutes. RTO: minutes.
- Cost: a meaningful fraction of production.
- Big advantage: you can send a small amount of real traffic to it continuously, which exercises it; still test the complete failover and full target load.

### 4. Multi-site active-active

Two or more regions serve production traffic simultaneously. Losing one means routing its share to the others.

- RPO: near zero (depends on replication mode). RTO: near zero.
- Cost: highest; each region must have headroom to absorb the others' load.
- Hard part: **data**. Writes in multiple regions need conflict resolution (DynamoDB global tables' default mode replicates asynchronously and uses last-writer-wins), or partitioning so each record has a single home region, or synchronous cross-region replication or consensus (Spanner, or DynamoDB's newer multi-Region strong consistency mode), which adds coordination latency determined by region placement and protocol, and can preserve acknowledged commits under the supported region-failure model. This does not prevent replicated logical corruption.

| Strategy | RPO | RTO | Cost |
|---|---|---|---|
| Backup/restore | hours | hours+ | £ |
| Pilot light | mins | 10s of mins | ££ |
| Warm standby | secs–mins | mins | £££ |
| Active-active | ~0 | ~0 | ££££ |

## Failover mechanics

Failover deserves explicit testing. Key questions:

- **Who decides?** Automatic failover reacts fast but can flap or trigger on false positives (a network partition makes the primary *look* dead). Many teams automate the mechanics but require a human to press the button for regional failover.
- **Split brain**: if the old primary isn't truly dead, two primaries accept writes. Use **fencing** (revoke the old primary's credentials or storage access) before promoting.
- **Capacity in the target**: the surviving region must take the whole load. For equal-capacity regions with evenly redistributed traffic and tolerance of one region loss, pre-failure utilization ceilings are 50% for two regions and about 67% for three. Reserve additional headroom for the desired latency.
- **DNS TTLs**: clients cache DNS. A freshly cached 300 s record can remain valid for five minutes; existing connections and client caching behavior can extend recovery. Preconfigured global routing can avoid waiting for DNS changes, but detection and reconnection still take time.
- **Data loss on promotion**: with async replication, writes that hadn't replicated are lost. That gap is the observed recovery-point loss; the RPO is the target it must meet.
- **Failback**: returning to the original region is a second migration, often forgotten in the plan.

> [!tip] Avoid control-plane dependencies during failover
> AWS's guidance is to rely on *data-plane* operations for failover (e.g. Route 53 health checks and pre-configured routing, which keep working) rather than control-plane actions like creating resources or editing records, which may be impaired during a regional event.

## Chaos engineering

You only know your DR and redundancy work if you've seen them work. **Chaos engineering** is the discipline of running controlled experiments on a system to build confidence that it withstands turbulent conditions.

Netflix's **Chaos Monkey** (built around 2010–11, open-sourced in 2012) randomly terminated production instances during business hours, forcing every team to build services that survive instance loss. Its successors simulated whole-zone (Chaos Gorilla) and region (Chaos Kong) failures.

The principles (from principlesofchaos.org):

1. Define **steady state** as a measurable output (e.g. successful plays per second), not internal metrics.
2. **Hypothesise** that steady state will continue in both control and experiment groups.
3. Introduce real-world events: kill instances, add latency, sever a dependency, fill a disk.
4. Try to **disprove** the hypothesis by looking for a difference in steady state.
5. Run in production where possible, **minimise blast radius**, and automate experiments to run continuously.

```
Experiment: "checkout survives loss
 of the recommendations service"
 Steady state: checkout success ≥ 99.5%
 Inject: 100% errors from recs, 5% users
 Abort if: checkout success < 99%
 Result: ✓ / ✗ → fix, re-run
```

### Game days

A **game day** is a scheduled exercise where a team simulates a disaster (e.g. "us-east-1 is gone") and executes the DR runbook for real. It tests people and process as well as systems: do on-call engineers know the steps, do they have the right access, is the runbook current? Google runs company-wide DiRT (Disaster Recovery Testing) exercises for this purpose.

## Key takeaways

- RPO is how much data you can lose; RTO is how long you can be down. Both are business decisions with costs.
- Replication isn't backup: keep immutable, isolated, point-in-time backups, and regularly test restores, timing them.
- DR strategies trade cost for speed: backup-restore, pilot light, warm standby, active-active.
- Failover is risky: fence old primaries to avoid split brain, account for DNS TTLs, use data-plane mechanisms, and plan failback.
- Chaos engineering and game days turn "we think it fails over" into "we've seen it fail over".

## Further reading

- [Disaster recovery options in the cloud (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Data integrity: what you read is what you wrote (Google SRE book)](https://sre.google/sre-book/data-integrity/)
- [Principles of chaos engineering](https://principlesofchaos.org/)
- [Chaos engineering (Wikipedia)](https://en.wikipedia.org/wiki/Chaos_engineering)
- [Disaster recovery (Wikipedia)](https://en.wikipedia.org/wiki/Disaster_recovery)
