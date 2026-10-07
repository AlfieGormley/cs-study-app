---
id: mem-tlb
title: The TLB and huge pages
level: intermediate
minutes: 13
summary: How the translation lookaside buffer makes paging fast, effective access time calculations, TLB reach, ASIDs and PCIDs across context switches, shootdowns, and when huge pages help or hurt.
---

The previous lesson ended with a problem. An uncached four-level x86-64 walk to a 4 KiB page reads four entries before the data access. That simplified read count is not a universal 5× latency prediction.

Hardware fixes this with a small, very fast cache of recent translations: the **translation lookaside buffer (TLB)**. Most memory accesses find their translation in the TLB and skip the walk entirely.

## What the TLB stores

Each TLB entry maps one virtual page to one physical frame, with the permission bits copied from the PTE:

```
 TLB entry
 +---------+---------+---------------+
 |   VPN   |   PFN   | R/W U/S NX .. |
 +---------+---------+---------------+
   tag       data      permissions
```

On every memory access the MMU does:

1. Look up the VPN in the TLB.
2. **Hit**: take the PFN, check permissions, and form the physical address. Many designs overlap lookup with cache indexing; actual latency and throughput depend on the CPU.
3. **Miss**: walk the page tables (the hardware **page walker** on x86 and ARM), insert the result into the TLB, then retry.

Some older architectures, notably MIPS, use a **software-managed TLB**: a miss raises an exception and the OS refills the entry itself. That gives the OS freedom over page-table format with handler cost depending on the architecture and implementation. x86 and ARM do it in hardware.

## Typical sizes and costs

TLB organizations differ by CPU, page size and instruction/data access type. Many cores have separate first-level instruction/data TLBs and another translation-cache level. Consult the exact CPU's documentation or hardware enumeration rather than assuming one capacity.

A miss served by another translation cache avoids a full walk. Page walks can use data caches and paging-structure caches; a TLB miss is not synonymous with a DRAM access or an OS page fault.

> [!note] Content gap
> Universal entry counts and cycle/microsecond costs are omitted: this lesson has no measured CPU configuration or reproducible benchmark record for those figures. The following capacities and times are explicit arithmetic examples.

## Why hit rates are high

The TLB works for the same reason caches work: **locality**.

> [!example] Scanning an array
> A loop reads a large array of 4-byte ints in order. Each 4 KiB page holds 1,024 ints.
>
> In a cold, aligned scalar-access model without translation prefetching or interfering evictions, the first access to each page misses and the next 1,023 hit. That is 1 miss per 1,024 accesses: a **99.9%** hit rate.
>
> Now read only one int per page (stride 4,096 bytes). Every access lands on a new page. On a cold pass without translation prefetching, each newly visited page misses. On repeated passes, capacity and replacement determine the hit rate.

```c
/* Same address range, different
   access counts and TLB miss rates. */
for (size_t i = 0; i < n; i++)
    sum += a[i];        /* stride 4 B */

for (size_t i = 0; i < n; i += 1024)
    sum += a[i];        /* stride 4 KiB */
```

On supported Linux PMUs, `perf stat -e dTLB-load-misses ./prog` can help investigate. Check `perf list`, event semantics, permissions and CPU model: a generic event need not count every L1-TLB miss.

Random access over a large data structure (a big hash table, a graph, a B-tree spread across GiB of RAM) is the hard case. Each access may touch a different page, and the TLB cannot hold them all.

## Effective access time

The **effective access time (EAT)** is the average cost of one memory access once TLB misses are included:

```
EAT = h * hit_cost + (1 - h) * miss_cost
```

where `h` is the TLB hit rate.

> [!example] Single-level table
> Memory access = 100 ns, TLB lookup time negligible, single-level page table, hit rate 98%.
> - Hit: 100 ns (just the data).
> - Miss: 100 ns for the PTE + 100 ns for the data = 200 ns.
> - EAT = 0.98 × 100 + 0.02 × 200 = 98 + 4 = **102 ns**, a 2% slowdown.

> [!example] x86-64, 4-level, no walk caching
> Same 100 ns memory, but a miss costs 4 table reads + the data = 500 ns.
> - At 99% hits: 0.99 × 100 + 0.01 × 500 = 99 + 5 = **104 ns**.
> - At 90% hits: 0.90 × 100 + 0.10 × 500 = 90 + 50 = **140 ns**, a 40% slowdown.

If the TLB lookup itself takes time `t` (older textbooks often use 20 ns), add `t` to both the hit and the miss cost. The lesson is the same: the hit rate dominates, and every percentage point of misses costs a multiple of itself once the walk is deep.

## TLB reach

**TLB reach** is the amount of memory the TLB can map at once: entries × page size.

| TLB | 4 KiB pages | 2 MiB pages |
|---|---|---|
| 64 entries | 256 KiB | 128 MiB |
| 1,536 entries | 6 MiB | 3 GiB |

A hot set beyond the effective reach can increase misses; locality, associativity, page-size-specific capacities and other translation-cache levels determine the rate. If all 50 GiB of a buffer pool is actively accessed, it greatly exceeds a hypothetical 6 MiB reach. Allocated pool capacity need not equal the hot working set. This is the main argument for huge pages.

## Context switches, ASIDs and PCIDs

A TLB entry says "VPN 0x400 maps to PFN 0x9a2". That is only true for one address space. When the kernel switches to another process (by loading CR3), the old entries become wrong.

The simple fix, and the traditional x86 behaviour, is to **flush the TLB** on every CR3 write. The new process then starts cold and pays a burst of misses.

Two features reduce the damage:

- **Global pages.** PTEs with the **G** bit set survive a CR3 write. Kernel mappings, identical in every process, were marked global so they stayed cached across switches.
- **Address-space identifiers.** Tags let translations from several address spaces coexist, reducing flushes. Mapping changes and tag reuse still require invalidation. ARM and MIPS call these **ASIDs**. On x86 they are **PCIDs** (process-context identifiers): 12 bits held in the low bits of CR3, so up to 4,096 tags.

```
 VPN    PFN    PCID
 0x400  0x9a2  3    <- process A
 0x400  0x177  5    <- process B
```

Linux on x86 assigns each CPU a small pool of PCIDs and recycles them across processes rather than giving every process a permanent tag. PCIDs help reduce **KPTI** overhead (lesson 1). When KPTI is active, a userspace system call switches between reduced user and full kernel page-table views. KPTI also works without PCIDs. With PCIDs, both sets of translations stay cached and the switches cost far less.

Threads in the same process share one address space, so switching between them needs no CR3 write and no flush.

## TLB shootdowns

Each CPU core has its own TLB. Suppose a process has threads on cores 0 to 7 and one thread calls `munmap` (or `mprotect` to remove write access). The kernel updates the page table, but cores 1 to 7 may still hold the old translation.

The kernel must perform a **TLB shootdown**:

1. Update the PTEs.
2. Send an **inter-processor interrupt (IPI)** to every other core that might be running this address space.
3. Each core invalidates the entries (`INVLPG` or a full flush) and acknowledges.
4. The initiating core waits for every acknowledgement before reusing the freed frames.

Shootdown cost varies with hardware, target CPUs and kernel policy. The IPI sequence above is a common implementation, not a requirement that every unmap interrupt every core; deferred invalidation and architectural broadcast mechanisms may differ. Workloads that `mmap` and `munmap` frequently in heavily threaded processes can spend real time here. That is one reason memory allocators avoid returning memory to the OS on every `free`, and why the kernel batches invalidations.

## Huge pages

A 2 MiB page needs one TLB entry for what would otherwise take 512 entries, and its page walk is one level shorter. Both help programs with large working sets.

Linux offers two mechanisms:

| | hugetlbfs | Transparent huge pages |
|---|---|---|
| Setup | Reserve at boot or via `vm.nr_hugepages` | Automatic |
| Sizes | Architecture-dependent; often 2 MiB/1 GiB on x86 | PMD-sized and supported smaller mTHP sizes |
| Swappable | No | Yes |
| Used by | DBs, DPDK, VMs | General apps |

For anonymous THP, `/sys/kernel/mm/transparent_hugepage/enabled` is a top-level policy inherited by configured sizes. Modern kernels also have per-size, process and mapping controls. In the simple inherited-policy case:

- `always`: eligible allocations may use THP, subject to size, mapping, process and allocation constraints.
- `madvise`: ordinary automatic allocation is limited to advised eligible regions.
- `never`: disables this automatic policy, but is not an absolute prohibition: `MADV_COLLAPSE` can bypass the sysfs setting, and per-size controls may differ. Use the documented process/mapping controls when full exclusion is required.

The kernel daemon **khugepaged** also scans memory and collapses runs of small pages into huge ones in the background.

### When huge pages hurt

- **Latency spikes.** Finding a free, aligned 2 MiB block may require **compaction** (moving pages around), which can stall an allocation by a workload-dependent amount.
- **Memory bloat.** A program that touches one byte in each of many 2 MiB regions may allocate a 2 MiB page per region instead of a base page, depending on policy and fault type. RSS can grow sharply for sparse workloads.
- **Copy-on-write amplification.** After `fork`, a write fault on a shared huge page can copy a larger unit, split a mapping, or reuse exclusive backing depending on kernel state and policy; it does not invariably copy 2 MiB. Redis forks to write snapshots, which is why the Redis docs advise disabling THP.

Choose THP or explicit HugeTLB based on measured workload and application guidance. PostgreSQL `huge_pages` controls explicit huge pages for its main shared-memory region, not a request for THP. Explicit reservations may fail and require sizing; reserved contiguous pages do not imply fragmentation is impossible elsewhere.

## How the TLB meets the cache

L1 data caches on most x86 cores are **virtually indexed, physically tagged**: the cache set is chosen from address bits inside the page offset (identical in virtual and physical addresses) while the TLB translates the upper bits in parallel. That is why L1 caches are small and many-way associative. The details belong to the Computer Architecture subject.

## Key takeaways
- TLBs cache translations and permissions. A miss can hit another translation-cache level or require a walk; cost depends on the CPU and mapping.
- Locality gives high hit rates for sequential access; random access over large memory can miss constantly.
- EAT = h × hit cost + (1 − h) × miss cost; with deep page tables, even a few per cent of misses is expensive.
- TLB reach = entries × page size; huge pages raise it 512-fold for 2 MiB pages.
- PCIDs and ASIDs tag entries by address space so context switches need not flush; PCIDs make KPTI affordable.
- Mapping removal requires coherent invalidation of stale translations; remote shootdowns commonly use IPIs.
- Huge pages can improve translation reach while adding compaction, memory and COW costs. Follow application-specific guidance and measure the workload.

## Further reading
- [OSTEP: Paging: Faster Translations (TLBs) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Transparent Hugepage Support — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [HugeTLB Pages — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/hugetlbpage.html)
- [Diagnosing latency issues (THP section) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [What Every Programmer Should Know About Memory, Ulrich Drepper (PDF)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
