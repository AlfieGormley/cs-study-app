---
id: mem-huge-page-policy
sourceLesson: mem-tlb
title: Choosing and measuring huge-page policies
level: intermediate
minutes: 3
summary: Huge pages can improve reach but also cause compaction, sparse-memory bloat and COW costs.
---

## Huge pages

A 2 MiB page needs one TLB entry for what would otherwise take 512 entries, and its page walk is one level shorter. Both help programs with large working sets.

Linux offers two mechanisms:

| | hugetlbfs | Transparent huge pages |
|---|---|---|
| Setup | Reserve at boot or via `vm.nr_hugepages` | Automatic |
| Sizes | Architecture-dependent; often 2 MiB/1 GiB on x86 | PMD-sized and supported smaller mTHP sizes |
| Swappable | No | Eligible anonymous backing can swap; paths vary |
| Used by | DBs, DPDK, VMs | General apps |

For anonymous THP, `/sys/kernel/mm/transparent_hugepage/enabled` is a top-level policy inherited by configured sizes. Modern kernels also have per-size, process and mapping controls. In the simple inherited-policy case:

- `always`: eligible allocations may use THP, subject to size, mapping, process and allocation constraints.
- **madvise mode**: ordinary automatic allocation is limited to advised eligible regions.
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
- Huge pages can improve reach but also cause compaction, sparse-memory bloat and COW costs.
- HugeTLB and transparent huge pages have different controls and reclaim properties.
- Application guidance and measurements matter more than a universal policy.

## Further reading
- [OSTEP: Paging: Faster Translations (TLBs) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Transparent Hugepage Support — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [HugeTLB Pages — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/hugetlbpage.html)
- [Diagnosing latency issues (THP section) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [What Every Programmer Should Know About Memory, Ulrich Drepper (PDF)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
