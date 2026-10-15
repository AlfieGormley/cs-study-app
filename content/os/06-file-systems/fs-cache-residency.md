---
id: fs-cache-residency
title: Page-cache residency and read-ahead
level: intermediate
minutes: 4
summary: Buffered I/O and ordinary shared file mappings use the page cache.
sourceLesson: fs-page-cache
---

A resident-memory access can avoid storage latency; the ratio depends on access pattern, hardware and queueing. So the kernel keeps recently used file data in RAM, in the **page cache**, and serves as many reads and writes from there as it can.

Ordinary buffered regular-file I/O normally uses the page cache; direct I/O, DAX and special files have different paths. Understanding it explains why the second run of a program is faster, why `free` says your RAM is "used", why `write` returns before the data is safe, and how cached I/O can reduce data movement in servers.

> [!note] Performance evidence gap
> No benchmark record accompanies the latency ratios or workload speed claims in this lesson. Fixed ratios and guaranteed timing outcomes are omitted; numeric scenarios below are illustrative models.

## What the page cache is

The page cache associates file offsets with cached memory, using an inode's mapping and page indices. Page size is architecture dependent; modern kernels can manage multiple pages together as folios. Ordinary buffered I/O and shared file mappings use the same backing cache. Private mappings can diverge on COW writes, and concurrency still needs synchronization.

```
 process      read(fd, buf, 4096)
                 |  copy
 kernel   +------v---------------+
          | page cache           |
          | (inode 7342, pg 0) --+--> hit
          | (inode 7342, pg 1)   |
          +----------+-----------+
                     | miss: I/O
                 storage device
```

On a **read**:

1. The VFS looks up the page for (inode, offset).
2. **Hit**: copy from the cached page into the user's buffer. No payload read from storage is needed for an up-to-date hit; metadata updates, faults in the destination buffer or other work can still occur.
3. **Miss**: allocate a page, ask the file system to read the block from the device, wait, then copy.

The cache uses whatever memory nothing else needs. That's why `free` shows little "free" memory on a busy machine:

```
$ free -h   (some columns omitted)
      total  used  free  cache  avail
Mem:   31Gi  6.2G  1.1G   24Gi   24Gi
```

The number to watch is **available**: free memory plus cache that can be dropped on demand. Reclaimable clean pages can be discarded without writing their file payload back, but locking, references, scanning and other constraints mean reclaim is not instantaneous or guaranteed for every page. Reclaim uses LRU-style active and inactive lists (or MGLRU on newer kernels).

> [!tip] Cold vs warm benchmarks
> A run with cold file pages may need storage reads; a subsequent run can benefit from cached data and metadata if they remain resident. Benchmark honestly by saying which state you measured. Linux exposes `drop_caches` for controlled test environments, but it changes system-wide cache state; use an isolated disposable test environment rather than a shared machine. This lesson does not run that operation.

## Read-ahead

If a process reads a file sequentially, the kernel guesses it will keep going and **reads ahead**: it fetches the following pages before they're asked for, so later reads hit the cache.

- The kernel detects sequential access per open file.
- Read-ahead grows according to kernel/filesystem heuristics and configured limits; it is not always simple doubling. Inspect the actual read_ahead_kb value instead of assuming a universal 128 KiB default.
- Random access shrinks or disables it, so it doesn't waste I/O.

```
$ cat /sys/block/nvme0n1/queue/read_ahead_kb
128
```

Applications can give hints with `posix_fadvise`:

| Advice | Effect |
|---|---|
| `SEQUENTIAL` | Bigger read-ahead |
| `RANDOM` | Disable read-ahead |
| `WILLNEED` | Hint to begin bringing a range into cache |
| `DONTNEED` | Advise releasing unneeded cached pages; not guaranteed eviction |

`DONTNEED` is handy for backup tools that read a terabyte once: it can reduce pollution from one-pass scans, but eviction policy and whether others need those same pages matter. Dirty or partial-page ranges may not be released.


## Key takeaways
- Buffered I/O and ordinary shared file mappings use the page cache.
- Available memory includes reclaimable cache; a warm run can avoid payload storage reads.

- Sequential access can trigger speculative reads.
- Fadvise gives advice rather than guaranteed eviction, especially for dirty or partial pages.


## Further reading
- [Page cache — Wikipedia](https://en.wikipedia.org/wiki/Page_cache)
- [Documentation for /proc/sys/vm (dirty_* settings) — kernel.org](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [open(2): O_DIRECT notes — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [posix_fadvise(2) — Linux manual page](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [sendfile(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sendfile.2.html)
- [Are You Sure You Want to Use MMAP in Your DBMS? — CIDR 2022](https://db.cs.cmu.edu/mmap-cidr2022/)
- [Zero-copy — Wikipedia](https://en.wikipedia.org/wiki/Zero-copy)
