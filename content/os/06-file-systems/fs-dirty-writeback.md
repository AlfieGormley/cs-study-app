---
id: fs-dirty-writeback
title: Dirty pages, thresholds and write stalls
level: intermediate
minutes: 5
summary: Buffered write completion does not guarantee persistence.
sourceLesson: fs-page-cache
---

This unit focuses on dirty pages, thresholds and write stalls. The preceding units provide the file and storage concepts used here.

## Write-back and dirty pages

A typical buffered write initially updates cached data, but the call can also trigger allocation, read-modify-write work, writeback or write throttling. It does not promise durability on ordinary completion:

1. Copy the bytes into the page cache (reading the page in first if the write covers only part of it).
2. Mark the page **dirty**.
3. Return after copying the reported byte count. Some data may already have reached storage, but persistence is not guaranteed.

The kernel's flusher threads write dirty pages back later. This is **write-back caching**. It makes writes fast, merges repeated writes to the same page into one I/O, and lets the file system allocate blocks in large runs (delayed allocation). The cost is that a crash loses whatever was still dirty, unless you called `fsync`.

When does write-back happen? These `vm` sysctls control it (illustrative configured values shown; inspect the running system). The two `_centisecs` settings are in **centiseconds**, hundredths of a second, and the two `_ratio` settings are percentages:

| Setting | Example value | Meaning |
|---|---|---|
| `dirty_expire_centisecs` | 3000 | Eligible for periodic writeback after 30 s |
| `dirty_writeback_centisecs` | 500 | Flusher wakes every 5 s |
| `dirty_background_ratio` | 10 | Start background flush at 10% |
| `dirty_ratio` | 20 | Writers blocked at 20% |

Converting the timer settings to seconds and the ratios to amounts of memory:

```formula
t = c / 100
t_expire = 3000 / 100 = 30 s
t_wake = 500 / 100 = 5 s
D_limit = (r / 100)M
D_limit = (20 / 100) × 64 GiB = 12.8 GiB
where
t: a time setting converted to seconds (s)
c: the setting's value in centiseconds (hundredths of a second)
t_expire: how old dirty data must be before periodic write-back picks it up (`dirty_expire_centisecs`)
t_wake: how often the flusher threads wake up (`dirty_writeback_centisecs`)
D_limit: the amount of dirty data at which a threshold kicks in, in gibibytes (GiB)
r: a `dirty_*_ratio` setting, as a percentage (here `dirty_ratio` = 20)
M: the dirtyable memory the kernel counts (see below); here assumed to be 64 GiB
s: second
GiB: gibibyte, 1,024^3 bytes, about 1.074 billion bytes
In words: 3000 centiseconds is 30 seconds, and a 20% ratio on 64 GiB of dirtyable memory lets about 12.8 GiB of unwritten data pile up before write throttling starts.
```

The ratios apply to the kernel's dirtyable-memory accounting (free/reclaimable memory with exclusions), not simply installed RAM or the displayed MemAvailable value. Per-device and cgroup writeback also affect behavior. In practice:

- Expiry controls when data becomes due for periodic writeback, not a minimum delay or durability deadline; other triggers can write earlier and congestion can delay completion.
- If dirty data passes `dirty_background_ratio`, flushing starts at once, in the background.
- If it reaches `dirty_ratio`, the writing process itself is subject to **write throttling**: it has to wait for write-back.

> [!example] The stall
> In a hypothetical workload, a machine with 64 GiB of RAM and the illustrated ratios can accumulate several gigabytes of dirty data. A job writes 20 GiB to a USB disk that manages 30 MB/s. `cp` races ahead while pages fill RAM, then hits `dirty_ratio` and stalls. When you unmount, `umount` waits minutes for the backlog to drain.

How long is "minutes"? Once the backlog is fixed, draining it is just size divided by speed:

```formula
t_drain = D / R
D = 12.8 GiB ≈ 13.7 × 10^9 B
t_drain ≈ 13.7 × 10^9 B / (30 × 10^6 B/s)
t_drain ≈ 458 s ≈ 7.6 min
where
t_drain: the time to write the whole dirty backlog to the disk, in seconds (s)
D: the dirty backlog, in bytes (B); here the 12.8 GiB `dirty_ratio` limit from above, converted with 1 GiB ≈ 1.074 × 10^9 B
R: the disk's sustained write rate, in bytes per second (B/s); here 30 MB/s = 30 × 10^6 B/s
GiB: gibibyte, 1,024^3 bytes
B: byte
s: second
min: minute, 60 s
≈: approximately equal to
In words: 13.7 billion bytes at 30 million bytes a second takes about 460 seconds, so unmounting can hang for around seven and a half minutes.
```

This assumes no new writes and a constant drain rate. It also shows a unit pitfall: gibibytes contain 1,073,741,824 bytes while disk megabytes contain one million bytes. Servers often set `dirty_background_bytes` and `dirty_bytes` to fixed, smaller values so that write-back is steadier and normal dirty-data accumulation is better bounded. Per-device limits, writeback errors and workload changes still prevent treating a configured threshold as an absolute cap.

`cat /proc/meminfo | grep -E 'Dirty|Writeback'` shows how much is pending right now.

## Key takeaways
- Buffered write completion does not guarantee persistence.
- Dirty timers control eligibility and wakeups, while dirty limits influence background flushing and writer throttling.

## Further reading
- [Page cache — Wikipedia](https://en.wikipedia.org/wiki/Page_cache)
- [Documentation for /proc/sys/vm (dirty_* settings) — kernel.org](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [open(2): O_DIRECT notes — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [posix_fadvise(2) — Linux manual page](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [sendfile(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sendfile.2.html)
- [Are You Sure You Want to Use MMAP in Your DBMS? — CIDR 2022](https://db.cs.cmu.edu/mmap-cidr2022/)
- [Zero-copy — Wikipedia](https://en.wikipedia.org/wiki/Zero-copy)
