---
id: mem-resident-metrics
sourceLesson: mem-in-practice
title: VSZ, RSS, PSS and private resident pages
level: advanced
minutes: 4
summary: VSZ describes address space, while RSS describes resident mappings and repeats shared charges.
---

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

The calculation applies page by page, since different pages can have different sharing counts. This example assumes one mapping per process for each shared page; Linux accounts using the relevant page-mapping counts, with additional large-page and accounting details. For the four workers:

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

Illustrative command/output sample; actual values depend on the workload, system and observation interval:

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

## Key takeaways
- VSZ describes address space, while RSS describes resident mappings and repeats shared charges.
- PSS apportions shared resident pages; USS describes private resident pages rather than guaranteed exit savings.
- MemAvailable estimates allocatable host memory more usefully than the free-page count alone.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
