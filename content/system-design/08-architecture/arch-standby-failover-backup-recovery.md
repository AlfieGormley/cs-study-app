---
id: arch-standby-failover-backup-recovery
title: Preparing standby failover and good backups
level: advanced
minutes: 3
summary: Compare standby warmth and exercise restore paths that replication alone cannot provide.
sourceLesson: arch-multi-region
---

The previous unit set recovery objectives. Active-passive keeps one authoritative serving region and prepares a standby; a successful restore must also survive logical mistakes.

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

### Recovering before a damaging change

If a faulty migration's deletes already reached the standby, promoting it does not recover the rows. Point-in-time recovery needs a suitable base backup and retained recovery logs to reconstruct the state just before the change. Later legitimate writes then need extraction and reconciliation; restoring old state discards them. Independently restricted backup access can reduce the chance that the same mistake or credential destroys both production state and its recovery material. Test restore integrity and duration, not just whether backup files exist.

## Key takeaways
- Standby warmth changes how much provisioning and capacity work remains during recovery.
- Fence the old writer, validate the standby and exercise routing, capacity and rollback.
- Replication copies bad writes as well as good ones; restore from a good base state plus retained logs when needed.
- Assess recoverable good state and reconciliation against the RPO rather than equating it to backup age.

## Further reading
- [AWS: Disaster recovery options in the cloud](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [PostgreSQL: Continuous archiving and point-in-time recovery](https://www.postgresql.org/docs/current/continuous-archiving.html)
