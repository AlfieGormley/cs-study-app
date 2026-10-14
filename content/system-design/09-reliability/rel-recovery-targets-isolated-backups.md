---
id: rel-recovery-targets-isolated-backups
title: Recovery targets and isolated backups
level: intermediate
minutes: 5
summary: Translate recovery objectives into restorable, isolated data copies.
sourceLesson: rel-disaster-recovery
---

Earlier units kept a serving path available during ordinary failures. Disaster recovery also handles region loss and logical corruption. The key question is whether you can recover a usable copy within the business’s data-loss and downtime limits.

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

Replication is not a backup. If someone deletes a table, replication normally propagates the deletion to replicas; timing and replay behavior vary. Backups protect against **logical failures** (bugs, mistakes, attacks) that replication copies.

Good backup practice:

- **Point-in-time recovery (PITR)**: periodic full snapshots plus continuous write-ahead log archiving. Postgres with WAL archiving, MySQL binlogs, and AWS RDS PITR can recover to supported points within the available, continuous backup/log history, up to the latest restorable point. Your RPO is set by how often log segments actually leave the server: RDS, for example, typically uploads logs every five minutes, so its latest restorable time is usually a few minutes behind.
- **3-2-1 rule**: 3 copies, on 2 different media or services, with 1 off-site.
- **Immutability**: enforced write-once retention (such as S3 Object Lock compliance mode) protects retained object versions from deletion, including by administrators. Governance mode can be bypassed by authorized users. Protect encryption keys too: immutable ciphertext is useless if its key is destroyed.
- **Separate account or project**: backups stored where the production credentials cannot reach.
- **Test restores regularly**. A backup that has never been restored is a hope, not a backup.

> [!warning] The restore you didn't test
> Google's SRE book chapter on data integrity makes the point bluntly: nobody really wants backups, they want restores. Automate restore tests and measure how long a full restore takes, because that time is your RTO floor for backup-based recovery.

### Restore time maths

Restore time often dominates RTO. The time to copy data back is its size divided by the speed you can actually restore at:

```formula
T = D / B
T = 20 TB / (500 MB/s)
T = 20,000,000 MB / (500 MB/s)
T = 40,000 s ≈ 11.1 h
where
T: the time to restore the data, in seconds (s) or hours (h)
D: the amount of data to restore, here 20 terabytes (TB)
B: the effective restore throughput (what you really get end to end, not the disk's rated speed), here 500 megabytes per second (MB/s)
TB: terabytes; 1 TB = 1,000,000 MB (decimal units)
MB: megabytes
MB/s: megabytes per second
s: seconds; 3,600 s = 1 h
h: hours
≈: approximately equal to (rounded)
In words: copying 20 TB back at 500 MB/s takes about 11 hours; provisioning and other independent recovery work may overlap, while dependent replay or validation adds time.
```

Plus applicable log replay, validation and any rebuild work required by the backup format; physical database backups generally already include indexes. If the business wants a 1-hour RTO, a restore-from-backup strategy can't meet it.

## Key takeaways

- RPO limits lost data in time; RTO limits downtime. Targets come from business needs.
- Replication also propagates destructive operations. Retain independent point-in-time recovery history.
- Use enforced retention, isolated credentials and protected keys; measure full restores including replay and validation.

## Further reading

- [Disaster recovery options in the cloud (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Data integrity: what you read is what you wrote (Google SRE book)](https://sre.google/sre-book/data-integrity/)
- [Disaster recovery (Wikipedia)](https://en.wikipedia.org/wiki/Disaster_recovery)
- [PostgreSQL continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [Amazon S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [Amazon RDS point-in-time recovery](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html)
