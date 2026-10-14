---
id: db-failover-fencing-history
title: Failover, fencing and lost history
level: intermediate
minutes: 2
summary: Promote a replica safely while preventing stale leaders and external identifiers from corrupting associations.
sourceLesson: db-replication
---

Failure detection does not prove the old leader has stopped. A safe promotion needs both a chosen surviving history and an enforced way to exclude stale writers.

## Failover

When the leader dies, a follower must be promoted.

1. **Detect** the failure, usually by missed heartbeats over some timeout (say 30 s).
2. **Choose** a new leader: ideally the most up-to-date follower. Agreeing on it is a consensus problem.
3. **Reconfigure** clients to write to the new leader (DNS, a proxy, or a service discovery update), and make sure the old leader, if it comes back, becomes a follower.

Tools: Patroni (Postgres, using etcd or Consul for leader election), MySQL Group Replication / Orchestrator, and managed services such as RDS Multi-AZ, whose failover duration depends on the service type, workload, recovery and client reconnection; measure it for the deployment.

What goes wrong:

- **Lost writes**: with async replication, unshipped writes from the old leader are discarded. A lagging promoted replica may reuse identifiers whose earlier values remain in caches or external systems, leading to incorrect associations. A specific historical incident attribution is omitted because this review did not establish its primary report.
- **Split brain**: the old leader isn't dead, just partitioned, and keeps accepting writes. Two leaders now diverge. Enforced fencing prevents stale writes. Leases require reliable enforcement/watchdogs, and epoch tokens work only when every protected resource rejects stale epochs.
- **Timeout tuning**: too short and you fail over during a GC pause or traffic spike (making things worse); too long and you're down for longer.

## Key takeaways
- Failover needs failure detection, a chosen leader and client reconfiguration.
- Async failover can discard acknowledged history that caches or other systems still reference.
- Fencing must actually prevent stale writes; cooperative self-demotion alone is insufficient.

## Further reading
- [www.postgresql.org: warm standby failover](https://www.postgresql.org/docs/current/warm-standby-failover.html)
- [Patroni: Watchdog support](https://patroni.readthedocs.io/en/latest/watchdog.html)
