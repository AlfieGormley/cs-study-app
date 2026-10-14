---
id: rel-dr-strategy-coordination-cost
title: Recovery strategies and coordination cost
level: intermediate
minutes: 3
summary: Choose a recovery strategy from tested targets, capacity and data-coordination limits.
sourceLesson: rel-disaster-recovery
---

Recovery objectives measure acceptable loss and downtime. The restore calculation in the previous unit provides a lower bound for backup-based recovery. Compare it with a rehearsed failover, not an assumed label such as “warm” or “active”.

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
- Cost: high in this planning spectrum; each region must have headroom to absorb the load displaced by the regional failures the design promises to tolerate.
- Hard part: **data**. Writes in multiple regions need conflict resolution (DynamoDB global tables' default mode replicates asynchronously and uses last-writer-wins), or partitioning so each record has a single home region, or synchronous cross-region replication or consensus (Spanner, or DynamoDB's newer multi-Region strong consistency mode), which adds coordination latency determined by region placement and protocol, and can preserve acknowledged commits under the supported region-failure model. This does not prevent replicated logical corruption.

| Strategy | RPO | RTO | Cost |
|---|---|---|---|
| Backup/restore | hours | hours+ | £ |
| Pilot light | mins | 10s of mins | ££ |
| Warm standby | secs–mins | mins | £££ |
| Active-active | ~0 | ~0 | ££££ |

## Key takeaways

- Backup/restore, pilot light, warm standby and active-active trade running cost for recovery work.
- Illustrative RPO/RTO bands are planning categories, never guarantees.
- Active-active still needs survivor headroom and an explicit multi-region write model; asynchronous writes can be lost.

## Further reading

- [Disaster recovery options in the cloud (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Disaster recovery (Wikipedia)](https://en.wikipedia.org/wiki/Disaster_recovery)
- [DynamoDB global table consistency modes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html)
