---
id: cache-restart-persistence
title: Budget persistence and warm restart memory
level: advanced
minutes: 3
summary: Compare RDB and AOF loss windows and estimate copy-on-write memory during a snapshot.
sourceLesson: cache-distributed
---

A disposable cache can still benefit from saved state: restarting warm avoids refilling every key from the database. Persistence has its own latency, loss-window and memory costs.

## Persistence

Memcached is ordinarily a volatile cache; optional warm restart preserves data over supported graceful restarts, not arbitrary crashes. Redis offers two persistence mechanisms:

| Mode | How | Loss on crash |
|---|---|---|
| RDB | Periodic snapshot via `fork()` | Since last snapshot |
| AOF `everysec` | Log every write, fsync 1/s | About 1 s |
| AOF `always` | fsync each write | Minimal; slow |
| None | Memory only | Everything |

**RDB** snapshots are compact and fast to load, but the `fork()` uses copy-on-write: under heavy writes, memory usage can nearly double while the snapshot runs. Every memory page the parent changes during the snapshot gets copied, so:

```formula reference
M_peak ≈ M × (1 + f)
where
M_peak: the peak memory used during the snapshot, in gigabytes (GB)
M: the memory the dataset uses normally, in GB
f: the fraction of memory pages written to while the snapshot runs, between 0 and 1
GB: gigabytes; 1 GB = 1,000,000,000 bytes
≈: approximately equal to
In words: the snapshot costs extra memory roughly equal to the share of pages modified while it runs; if every page is touched, memory doubles.
```

This first-order estimate excludes non-dataset allocations, buffers, allocator fragmentation, page-size effects and other process overhead. A 26 GB dataset on a 32 GB machine may fit normally, but if 30% of its pages are rewritten during the snapshot it needs about 34 GB and can be killed for running out of memory. The danger grows with write rate and snapshot duration, not just dataset size. Leave headroom (do not run Redis at 95% of RAM with RDB enabled).

**AOF** (append-only file) logs every write command, and is periodically rewritten to stay compact. Many deployments use both: AOF for durability, RDB for backups and fast restarts.

Why would a cache want persistence? **Warm restarts.** A 200 GB cache that restarts empty can take hours to refill and floods the database while doing so. Loading a saved state can reduce refill pressure, but restart and refill durations require measurement.

## Key takeaways
- RDB restores snapshots; AOF logs writes with a durability/latency trade-off selected by its fsync policy.
- Forked snapshots copy pages changed during the snapshot and can require substantial memory headroom.
- Copy-on-write arithmetic is a first-order model; measure buffers, fragmentation and restart times for the actual deployment.

## Further reading
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Warm restart — Memcached](https://docs.memcached.org/features/restart/)
