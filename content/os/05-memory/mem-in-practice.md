---
id: mem-in-practice
title: Overcommit, OOM, RSS and cgroups in production
level: advanced
minutes: 16
summary: How overcommit changes allocation failure on Linux, how the OOM killer picks a victim, what VSZ, RSS, PSS and USS really measure, how cgroup v2 and Kubernetes limit memory, and the tools for hunting leaks.
---

The earlier lessons built the machinery. This one is about living with it on real servers: reading memory numbers correctly, understanding why a process was killed, and setting limits that hold.

Three facts drive most production surprises:

1. Linux can permit commitments beyond available physical backing (**overcommit**), according to policy.
2. Severe allocation pressure can cause reclaim, allocation failure or an **OOM kill**, depending on context and policy.
3. Every common memory metric measures something slightly different from what people assume.

## Overcommit and delayed failure

A successful `malloc` or `mmap` need not make every requested byte resident. Existing allocator pages, metadata and population flags can already consume memory; new anonymous backing is often supplied on first touch. So the kernel faces a choice at allocation time: should it promise memory it does not yet have?

The policy is `vm.overcommit_memory`:

| Mode | Behaviour |
|---|---|
| 0 (default) | Heuristic: refuse only obviously impossible requests |
| 1 | Skip the overcommit admission check; other limits and allocation failures still apply |
| 2 | Strict: refuse beyond a commit limit |

Mode 0 applies a heuristic, not a guarantee that each request below RAM succeeds. Resource limits, address-space availability, mapping limits, metadata allocation and current memory conditions can still reject requests.

> [!example] Promises versus reality
> A box has 16 GiB of RAM and no swap. A program calls `malloc(8 GiB)` ten times. Assume all ten allocations succeed under the current limits and heuristic. They request 80 GiB, far more than the available backing.
>
> Nothing goes wrong until the program writes to the memory. If those pages must remain backed and reclaim cannot satisfy demand, allocation can fail or trigger OOM handling before the requested 80 GiB is populated. Other users of memory and policy determine when and what happens.

Why would anyone want this? Because most programs reserve far more than they use: large mostly unused thread-stack reservations and mostly untouched, sparse arrays, JVM heaps reserved up front, and above all `fork`. An ordinary fork can share private writable data through copy-on-write. Strict accounting reserves for eligible writable private mappings that the child could copy; it does not simply duplicate VSZ or RSS, and special mappings have exceptions. Overcommit lets that `fork` succeed.

### Strict mode

In mode 2 the kernel tracks **Committed_AS** (total promised) and refuses allocations that would push it over **CommitLimit**. The limit counts all of swap but only a percentage of RAM:

```formula
CommitLimit = S_swap + R × r / 100
Committed_AS + A ≤ CommitLimit
where
CommitLimit: the most memory the kernel will promise in strict mode, shown in /proc/meminfo
S_swap: the total swap space
R: the usable RAM: physical RAM minus pages reserved for HugeTLB
r: vm.overcommit_ratio, the percentage of RAM that counts; 50 by default
Committed_AS: the memory already promised to all processes, also shown in /proc/meminfo
A: the size of the new commitment being requested
≤: less than or equal to; a request that would break this fails with ENOMEM
In words: strict mode adds all of swap to a fixed percentage of RAM, and refuses any allocation that would take the total promised past that limit.
```

A nonzero `vm.overcommit_kbytes` supplies an absolute RAM contribution instead of the ratio. Per-user/admin reserves can further restrict admission.

> [!example] Calculating the limit
> 64 GiB of RAM, 8 GiB of swap, ratio 50, no HugeTLB reservation and overcommit_kbytes zero.

```formula
CommitLimit = 8 GiB + 64 GiB × 50 / 100
CommitLimit = 8 GiB + 32 GiB = 40 GiB
where
CommitLimit: the strict-mode commit limit
GiB: gibibyte, 2^30 bytes
In words: all 8 GiB of swap plus half of the 64 GiB of RAM gives a 40 GiB limit.
```

Even with 30 GiB of RAM physically free, an allocation that pushes the committed total past 40 GiB fails with `ENOMEM`.

Both numbers are visible in `/proc/meminfo`. Strict admission can make insufficient commitment visible as an allocation error, but does not rule out cgroup OOM or every later failure. RAM outside the commit limit is not necessarily wasted: file-backed cache and kernel users can use it. Large forks can fail admission. Redis recommends mode 1 to avoid this particular overcommit rejection; fork can still fail for other reasons and COW still needs real headroom.

## The OOM killer

Some allocation failures invoke the **OOM killer** after permitted reclaim paths are exhausted. Others return failure, retry or follow configured panic policy. The ordinary victim-selection path compares eligible tasks within the relevant scope and sends SIGKILL; special cases such as killing the allocating task or an existing exiting victim can change the code path.

The score (`oom_badness`) is roughly the process's memory footprint as a share of what is available: its **RSS, swap usage and page tables**. Then the admin's bias is added:

- `/proc/<pid>/oom_score_adj` ranges from **−1000 to +1000**. In the simplified score, each unit adds one-thousandth of the applicable memory allowance; scope can be system-wide, cpuset/NUMA constrained or cgroup limited. +500 adds half that allowance, not necessarily half physical RAM.
- **−1000** exempts a process entirely. Service policies can set negative values to influence relative selection; verify the actual unit and process settings.
- `/proc/<pid>/oom_score` shows a rescaled form of the current score, including the adjustment.

In simplified form, with memory measured as a share of the allowance in thousandths:

```formula
S ≈ 1000 × M / T + a
where
S: the badness score; the eligible process with the highest score is killed
≈: approximately equal to (the kernel works in pages and rounds)
M: the process's memory: resident pages (RSS) plus swap entries plus page-table pages
T: the memory allowance for the scope: RAM plus swap system-wide, or the limit of the cgroup or cpuset
a: oom_score_adj, from −1000 to +1000 (−1000 instead exempts the process entirely)
In words: a process's share of the allowance, scaled to 0–1000, plus the admin's adjustment; +500 is worth half of the allowance.
```

For example, with a 16 GiB allowance, a 6 GiB process with no adjustment scores about 1000 × 6 / 16 = 375, while a 2 GiB process with +500 scores about 125 + 500 = 625 and is killed first.

The kill leaves a trail in the kernel log:

```
$ dmesg | grep -i oom
Out of memory: Killed process 4121
(java) total-vm:9123456kB,
anon-rss:7340032kB, file-rss:0kB,
oom_score_adj:0
```

Badness is not simply largest RSS: swap, page tables, adjustments and which tasks are eligible all matter. User-space tools can act on pressure before kernel OOM. **systemd-oomd** can target cgroups using configured pressure policy; **earlyoom** normally selects processes using available-memory/swap thresholds and process scores. Neither guarantees an earlier kill in every workload.

## Reading memory numbers

`ps` and `top` show two numbers per process, and both mislead in different ways:

| Metric | Measures |
|---|---|
| VSZ (VIRT) | Size of all mapped address space |
| RSS (RES) | Pages currently resident in RAM |
| PSS | RSS with shared pages split between sharers |
| USS | Resident pages reported as private to the process |

- **VSZ** counts reserved-but-untouched memory, mapped files and glibc's 64 MiB arena reservations. A 30 GiB VSZ is often harmless.
- **RSS** counts a shared page fully in *every* process that maps it. Summing RSS over 50 worker processes that share 200 MiB of libraries counts that 200 MiB fifty times.
- **PSS** divides each shared page by the number of processes sharing it. Summing PSS over all relevant sharers approximates the resident pages represented by those mappings; it excludes unmapped cache and other kernel memory and has accounting/rounding caveats.
- **USS** is private resident memory, not a promise of how much RAM becomes free on exit. Private file-backed cache can remain cached, and kernel resources released on exit are not all in USS.

> [!example] PSS by hand
> Four Gunicorn workers each have 40 MiB private memory and share 100 MiB of resident copy-on-write pages. Assume only these four workers still map them; the master has exited or unmapped that region.

When a group of processes share the same pages, the three per-process metrics are:

```formula
RSS = U + S
PSS = U + S / N
USS = U
where
RSS: resident set size of one process
U: the process's private resident memory
S: the resident memory it shares with the others
PSS: proportional set size: shared pages divided among the sharers
N: the number of processes sharing those pages
USS: unique set size: private resident memory only
In words: RSS charges every sharer the whole shared amount, PSS charges each an equal slice, and USS ignores shared pages entirely.
```

The real formula applies page by page, since different pages can have different numbers of sharers. For the four workers:

```formula
RSS = 40 MiB + 100 MiB = 140 MiB
PSS = 40 MiB + 100 MiB / 4 = 65 MiB
T_RSS = 4 × 140 MiB = 560 MiB
T_PSS = 4 × 65 MiB = 260 MiB
where
RSS: each worker's resident set size
PSS: each worker's proportional set size
T_RSS: the sum of RSS over the four workers
T_PSS: the sum of PSS over the four workers
MiB: mebibyte, 2^20 bytes
In words: summing RSS counts the shared 100 MiB four times (560 MiB), while summing PSS counts it once (260 MiB), the real cost. Each worker's USS is its 40 MiB of private memory.
```

Linux gives the breakdown directly:

```
$ grep -E 'Rss|Pss' \
    /proc/4121/smaps_rollup
Rss:          1428356 kB
Pss:           912004 kB
Pss_Anon:      880112 kB
Pss_File:       31892 kB
```

`/proc/<pid>/status` splits RSS into **RssAnon** (resident anonymous mappings, including heap and stack), **RssFile** (resident file mappings; clean reclaimable pages may be dropped and reread) and **RssShmem**. `smem` reports PSS and USS across processes.

For the whole machine, ignore "free" in `free -h` and read **available** (`MemAvailable`): the kernel's estimate of how much could be allocated without swapping, including reclaimable page cache.

## cgroup v2 memory limits

Containers do not get their own kernel or their own OOM killer; they get a **cgroup**. The memory controller accounts for anonymous memory, file cache and many kernel allocations. Shared pages normally have one owning cgroup charge rather than a full charge to every accessor; accounting scope and special memory types have exceptions.

The main files in `/sys/fs/cgroup/<group>/`:

| File | Purpose |
|---|---|
| `memory.current` | Usage now, cache included |
| `memory.max` | Hard limit |
| `memory.high` | Throttle point |
| `memory.min` / `.low` | Protection from reclaim |
| `memory.events` | Counts of high, max, oom_kill |

What happens as usage rises:

1. Past **memory.high**: the group's tasks are made to reclaim their own memory and are slowed down. Crossing high does not itself invoke the kernel OOM killer. Independent global/ancestor pressure or a user-space OOM policy can still kill tasks.
2. At **memory.max**: charged allocations may trigger reclaim within the constrained subtree. If the limit cannot be met, eligible allocation paths can invoke cgroup OOM; some allocations instead fail. Victims stay within the constrained subtree. `memory.oom.group` requests group killing, with exceptions including tasks protected by oom_score_adj=-1000.

So a container can be OOM-killed while the host has plenty of free RAM. `memory.events` will show `oom_kill` incrementing, and `memory.stat` breaks usage into anon, file, kernel and more.

> [!warning] Page cache counts
> A container reading a large file can accumulate a page-cache charge, depending on ownership, readahead and reclaim. Clean cache that is not pinned in place is reclaimable, but the file counter alone does not prove that usage is safe or all reclaim can succeed. But dirty pages and tmpfs (`/dev/shm`, `emptyDir` with `medium: Memory`) cannot simply be dropped, and tmpfs counts against the limit like anonymous memory.

### Kubernetes

A container's `resources.limits.memory` becomes its cgroup's `memory.max`. `requests.memory` is used by the scheduler to place pods (and, with the optional MemoryQoS feature, to set protection).

A limit-related OOM can kill a container process, commonly reported as **OOMKilled** with code **137**, following the usual shell convention for a process killed by a signal:

```formula
c = 128 + s
c = 128 + 9 = 137
where
c: the exit code reported for a process killed by a signal
s: the signal number; SIGKILL is 9 and SIGTERM is 15 (giving 143)
In words: an exit code above 128 means "killed by signal number code minus 128", so 137 means SIGKILL.
```

 Code 137 alone does not prove OOM, and OOMKilled alone does not prove the container's own limit was the cause: node/global OOM is possible. **Kubelet eviction** is separate; memory-pressure ranking considers whether usage exceeds requests, Pod Priority, and usage relative to requests.

### Runtimes in containers

Managed runtimes must size themselves to the cgroup, not the host:

- **JVM**: supported HotSpot versions can use container limits in heap ergonomics, but cgroup-version support, vendor/version and flags matter. MaxRAMPercentage commonly defaults to 25, with small-memory and other ergonomics affecting actual heap sizing. Metaspace, stacks, JIT, GC structures and native/direct buffers need additional room. Verify the running JVM's detected limit and flags.
- **Go**: `GOMEMLIMIT` (Go 1.19+) sets a soft budget for memory managed by the Go runtime; it excludes some external memory and may be exceeded to avoid excessive GC.
- **Node.js**: `--max-old-space-size` limits V8 old-space, not the entire heap or total process RSS.

Budget measured non-heap peaks, cache and allocation spikes below the container limit. A fixed 20–30% margin is not a guarantee for every runtime or workload.

## Finding leaks

A leak is memory that is allocated, never freed, and no longer useful. Persistent RSS/PSS growth can motivate investigation but neither proves a leak nor catches every leak. Before blaming a leak, rule out allocator retention (lesson 6) and caches that are simply warming up.

| Tool | Scope | Requirement |
|---|---|---|
| Valgrind Memcheck | Native memory checks | Supported platform, instrumented execution |
| ASan + LSan | Native memory errors / unreachable allocations | Supported toolchain, build instrumentation |
| heaptrack / bcc memleak | Native allocation history / outstanding allocations | Compatible hooks and permissions |
| jemalloc profiling | Sampled allocator stacks | Profiling-enabled allocator configuration |
| tracemalloc | Traced Python allocations | Enable before allocations of interest |

> [!note] Measurement gap
> No representative overhead measurements accompany this lesson. Fixed slowdown factors and claims that a tool is automatically safe for production are omitted. Benchmark the selected configuration and sampling rate.

AddressSanitizer is compiled in (`-fsanitize=address`) and, on Linux, runs LeakSanitizer at exit to report unreachable blocks with their allocation stacks. Valgrind generally needs no rebuild for instrumentation, though debug information improves reports. bcc memleak can attach to supported allocation functions, recording outstanding allocations observed after attachment; it does not by itself determine reachability or reconstruct all earlier allocations.

In Python, `tracemalloc` compares snapshots and points at the line responsible:

```python
import tracemalloc

cache = []

def handle(req):
    cache.append(b"x" * 10_000)  # leak

tracemalloc.start()
before = tracemalloc.take_snapshot()
for i in range(1000):
    handle(i)
after = tracemalloc.take_snapshot()

top = after.compare_to(before, "lineno")
print(top[0])
# Output varies with Python and platform.
```

The payload size works out as:

```formula
D = 1,000 × 10,000 B = 10,000,000 B
D = (10,000,000 / 2^20) MiB ≈ 9.54 MiB
where
D: the total payload bytes appended to the cache
B: bytes
MiB: mebibyte, 2^20 = 1,048,576 bytes
≈: approximately equal to
In words: a thousand 10,000-byte objects is 10 million bytes, about 9.54 MiB (9,765.625 KiB), plus object and list overhead.
```

Python reports in binary units, so expect about 9.5 MiB, not 10. Snapshot attribution and exact counts vary by Python version and allocator. In garbage-collected languages the usual "leak" is exactly this: a reachable collection, cache or listener list that only ever grows.

## A debugging checklist

When a service's memory looks wrong:

1. **Which number?** VSZ, RSS, PSS or `memory.current`? Each answers a different question.
2. **Anon or file?** RssAnon includes anonymous mappings beyond the heap. RssFile and cgroup file counters cover different scopes; inspect dirty, writeback, shmem, reclaim and pressure before calling growth harmless.
3. **Killed by whom?** `dmesg` for the kernel OOM killer, `memory.events` for a cgroup limit, kubelet events for eviction, the systemd journal for systemd-oomd.
4. **Leak or retention?** Compare the allocator's statistics or a heap profile with RSS.
5. **Is the limit right?** Heap cap plus non-heap overhead plus headroom must fit under `memory.max`.

## Key takeaways
- Linux defaults to heuristic overcommit; allocation may fail immediately or later. Strict overcommit accounting uses ratio/absolute-budget settings and applicable reservations.
- Ordinary OOM selection scores eligible tasks in its scope using resident, swapped and page-table usage plus adjustment; context and policies add exceptions.
- VSZ counts address space, RSS double-counts shared pages, PSS apportions shared resident mappings, USS measures private resident pages rather than guaranteed exit savings; for the machine, read MemAvailable.
- cgroup v2 charges page cache to the group; memory.high throttles, memory.max reclaims then OOM-kills inside the group; Kubernetes cgroup-v2 limits commonly map to memory.max; exit 137 alone does not identify OOM.
- Runtimes need heap caps well below the container limit because of non-heap memory.
- Find leaks with ASan/LSan, Valgrind, eBPF memleak, jemalloc profiling or tracemalloc, after ruling out allocator retention and warming caches.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
