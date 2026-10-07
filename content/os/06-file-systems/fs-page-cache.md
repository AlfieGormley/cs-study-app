---
id: fs-page-cache
title: The page cache and buffering
level: intermediate
minutes: 14
summary: How Linux caches file data in RAM, read-ahead and write-back, dirty pages and the knobs that control them, O_DIRECT, mmap versus read, and zero-copy with sendfile.
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

The number to watch is **available**: free memory plus cache that can be dropped on demand. Reclaimable clean pages can be discarded without writing their file payload back, but locking, references, scanning and other constraints mean reclamation is not instantaneous or guaranteed for every page. Reclaim uses LRU-style active and inactive lists (or MGLRU on newer kernels).

> [!tip] Cold vs warm benchmarks
> A run with cold file pages may need storage reads; a subsequent run can benefit from cached data and metadata if they remain resident. Benchmark honestly by saying which you measured, or empty the cache first with `sync; echo 3 > /proc/sys/vm/drop_caches` (as root, never in production).

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

## Write-back and dirty pages

A typical buffered write initially updates cached data, but the call can also trigger allocation, read-modify-write work, writeback or throttling. It does not promise durability on ordinary completion:

1. Copy the bytes into the page cache (reading the page in first if the write covers only part of it).
2. Mark the page **dirty**.
3. Return after copying the reported byte count. Some data may already have reached storage, but persistence is not guaranteed.

The kernel's flusher threads write dirty pages back later. This is **write-back caching**. It makes writes fast, merges repeated writes to the same page into one I/O, and lets the file system allocate blocks in large runs (delayed allocation). The cost is that a crash loses whatever was still dirty, unless you called `fsync`.

When does write-back happen? These `vm` sysctls control it (illustrative configured values shown; inspect the running system):

| Setting | Example value | Meaning |
|---|---|---|
| `dirty_expire_centisecs` | 3000 | Eligible for periodic writeback after 30 s |
| `dirty_writeback_centisecs` | 500 | Flusher wakes every 5 s |
| `dirty_background_ratio` | 10 | Start background flush at 10% |
| `dirty_ratio` | 20 | Writers blocked at 20% |

The ratios apply to the kernel's dirtyable-memory accounting (free/reclaimable memory with exclusions), not simply installed RAM or the displayed MemAvailable value. Per-device and cgroup writeback also affect behavior. In practice:

- Expiry controls eligibility for periodic writeback, not a minimum delay or durability deadline; other triggers can write earlier and congestion can delay completion.
- If dirty data passes `dirty_background_ratio`, flushing starts at once, in the background.
- If it reaches `dirty_ratio`, the **writing process itself is throttled** and has to wait for write-back.

> [!example] The stall
> In a hypothetical workload, a machine with 64 GiB of RAM and the illustrated ratios can accumulate several gigabytes of dirty data. A job writes 20 GiB to a USB disk that manages 30 MB/s. `cp` races ahead while pages fill RAM, then hits `dirty_ratio` and stalls. When you unmount, `umount` waits minutes for the backlog to drain. Servers often set `dirty_background_bytes` and `dirty_bytes` to fixed, smaller values so that write-back is steadier.

`cat /proc/meminfo | grep -E 'Dirty|Writeback'` shows how much is pending right now.

## Bypassing the cache: O_DIRECT

Opening a file with `O_DIRECT` asks the kernel to move data **directly between your buffer and the device**, skipping the page cache.

Who wants that? Databases with their own cache. MySQL's InnoDB has a buffer pool, Oracle and ScyllaDB manage their own memory, and caching the same page again in the kernel would waste RAM (**double buffering**) and add a copy. InnoDB on Linux is commonly configured with `innodb_flush_method=O_DIRECT`.

PostgreSQL takes the other path: it uses buffered I/O and relies on the page cache alongside its own `shared_buffers`, which is why the usual advice is to give `shared_buffers` only around a quarter of RAM.

The rules and caveats of `O_DIRECT`:

- Buffer address, file offset and length can have alignment requirements that are not universally identical to the device's logical block size. Requirements vary by filesystem/kernel/file and can be queried via STATX_DIOALIGN where supported. Misalignment can fail with EINVAL or fall back to buffered I/O.
- Direct I/O avoids ordinary page-cache hits and read-ahead. Application caching/batching, block-layer merging, device behavior and workload determine performance; it is not universally slower.
- It is **not** a durability guarantee. The data may still sit in the device's volatile cache, and file metadata (size, block allocation) isn't flushed. You still need `fsync` or `O_DSYNC`.

## mmap vs read

`mmap` maps a file into your address space. Instead of copying from the page cache into your buffer, ordinary file-backed mappings can initially reference the file's cached pages; private writes can create COW copies. Language-level operations such as Python slicing may still copy data.

```python
import mmap

with open("big.bin", "rb") as f:
    m = mmap.mmap(f.fileno(), 0,
                  access=mmap.ACCESS_READ)
    header = m[:16]   # copies 16 bytes
    n = m.find(b"needle")
    m.close()
```

An access without a present usable translation causes a **page fault**. Prefaulting, fault-around and population options mean not every first page touch necessarily faults separately. The kernel finds or loads the page and installs a mapping; after that, access is a plain memory load.

| | `read()` | `mmap` |
|---|---|---|
| Copy into user buffer | yes | no |
| Access path | syscall per read call, then loads from buffer | ordinary loads once mapped |
| Cost per new page | in syscall | page fault |
| I/O errors | return code | `SIGBUS` |
| Eviction | kernel policy, advisory hints | kernel policy, advisory hints |

`mmap` shines for random access to files that fit comfortably in RAM, for sharing read-only data between processes (shared libraries are mapped this way), and for convenience.

It has real costs at scale:

- **Page faults and TLB shootdowns.** Unmapping or evicting pages across many cores may require translation invalidation and inter-CPU coordination; exact mechanisms and costs vary.
- **Errors arrive as signals.** A disk error or a file truncated by someone else turns a memory access into `SIGBUS`, which is hard to handle.
- **No control over write-back.** A modified page can be written to disk at any moment, so a database must enforce WAL ordering before dirtying shared mapped data or use a design that preserves ordering through another mechanism. This is a design constraint, not proof that every mmap database is incorrect.

The CIDR 2022 paper "Are You Sure You Want to Use MMAP in Your DBMS?" documents these problems in databases that started with `mmap` and later moved away (MongoDB's original storage engine was one example).

## Zero-copy: sendfile

A static file server's inner loop looks like this:

```python
while chunk := os.read(fd, 65536):
    sock.sendall(chunk)
```

Count the copies for each chunk:

```
 disk --DMA--> page cache
 page cache --CPU--> user buffer
 user buffer --CPU--> socket buffer
 socket buffer --DMA--> NIC
```

In this simplified uncached conventional path there are two CPU copies plus device transfers, with read/send calls per chunk. Actual copy and syscall counts depend on cache state, short transfers, offloads and implementation. The data never needed to visit user space.

`sendfile(out_fd, in_fd, offset, count)` asks the kernel to move data from a file to a socket directly:

```python
os.sendfile(sock.fileno(), fd,
            offset, count)
```

```
 disk --DMA--> page cache
 page cache --> NIC (DMA gather)
```

With a network card that supports scatter-gather DMA, the kernel just hands the NIC pointers to the page cache pages. This can eliminate payload copies through user space and, with a suitable implementation, CPU payload copies on the transmit path. The exact copying depends on offloads, transforms and fallback paths; zero-copy is a path capability, not a universal count guarantee.

Real uses:

- **Kafka** can use file-transfer paths for suitable plaintext log delivery; encryption, conversion and configuration can select other paths.
- **nginx** has `sendfile on;` for static files.
- `splice` and `vmsplice` generalise the idea through pipes.

The catch: the kernel sends the bytes as they are. If you need to compress or encrypt them in user space, as with TLS, you lose the benefit, unless you use kernel TLS (kTLS), which lets the kernel encrypt during `sendfile`.

## Where async I/O fits

Buffered hits can avoid payload-storage latency. Writes can block on throttling, allocation or I/O, and synchronous read misses can wait for data. Thread pools, `epoll` (for sockets) and `io_uring` (for files and sockets) exist to overlap many such operations. They're the subject of the next module.

## Key takeaways
- The page cache holds file pages in otherwise-unused RAM; reads that hit it need no I/O, and "available" memory includes cache that can be dropped.
- Read-ahead detects sequential access and fetches pages early; `posix_fadvise` lets programs steer it.
- Buffered writes initially update cached pages but can block or trigger I/O; expiry is writeback eligibility, not a durability deadline. Dirty thresholds influence throttling.
- `O_DIRECT` bypasses the cache for databases with their own buffer pools; it needs aligned I/O and still isn't a durability guarantee.
- mmap can avoid read-buffer copies but needs fault/error handling and a design that accounts for shared-page writeback.
- `sendfile` sends file data to a socket without passing through user space, the basis of Kafka's and nginx's efficiency.

## Further reading
- [Page cache — Wikipedia](https://en.wikipedia.org/wiki/Page_cache)
- [Documentation for /proc/sys/vm (dirty_* settings) — kernel.org](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [open(2): O_DIRECT notes — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [posix_fadvise(2) — Linux manual page](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [sendfile(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sendfile.2.html)
- [Are You Sure You Want to Use MMAP in Your DBMS? — CIDR 2022](https://db.cs.cmu.edu/mmap-cidr2022/)
- [Zero-copy — Wikipedia](https://en.wikipedia.org/wiki/Zero-copy)
