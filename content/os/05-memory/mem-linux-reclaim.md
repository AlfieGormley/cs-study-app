---
id: mem-linux-reclaim
sourceLesson: mem-page-replacement
title: Linux reclaim lists, generations and stalls
level: intermediate
minutes: 3
summary: Classic active/inactive lists and refault history help resist one-pass scans.
---

## How Linux does it

Linux does not run a textbook clock. Its classic design keeps, per memory node and per cgroup, separate LRU lists for **anonymous** and **file** pages, each split into **active** and **inactive**:

```
new page
   |
   v
inactive --- used again ---> active
   |     <------ demote ------
   v
 evict
```

- In the classic design, file-page admission to inactive lists and promotion based on observed reuse help resist one-pass scans. Refault handling and access paths add exceptions; active pages are not immune to pressure or scans.
- Reclaim scans the tail of the inactive lists, checking A bits (through the reverse map from page to PTEs). Referenced pages get another chance; unreferenced ones are evicted.
- When the active list is too large, pages are demoted from it.
- **Refault detection**: when an evicted file page is faulted back in, the kernel works out how long it was gone (from a shadow entry left in the page cache). Refault distance and related history can influence activation. This is a workload-size/eviction-history signal, not simply elapsed wall-clock time.

Since Linux 6.1 there is also the **multi-generational LRU (MGLRU)**, from Google. It sorts pages into several generations by age rather than two lists and scans page tables more efficiently. Its documentation describes how pages move to older generations, eviction and refault feedback for workload-dependent reclaim decisions. Distros choose whether to enable it (`/sys/kernel/mm/lru_gen/enabled`).

### When reclaim runs

Each memory zone has three **watermarks**: min, low and high.

- Free memory drops below **low**: the background thread **kswapd** wakes and reclaims until free memory reaches **high**.
- An allocation that cannot be satisfied may enter **direct reclaim** if its allocation flags allow it. Watermarks are part of that decision; memory-cgroup limits, fragmentation, allocation order and reclaim restrictions also matter. Not every allocation below min performs reclaim. This is a common source of mysterious latency spikes.

`vm.min_free_kbytes` and `vm.watermark_scale_factor` tune these levels.

## Key takeaways
- Classic active/inactive lists and refault history help resist one-pass scans.
- MGLRU uses generations and feedback when enabled.
- Background reclaim and allocation-time reclaim have different latency effects.

## Further reading
- [OSTEP: Beyond Physical Memory: Policies (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Page replacement algorithm — Wikipedia](https://en.wikipedia.org/wiki/Page_replacement_algorithm)
- [Bélády's anomaly — Wikipedia](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)
- [Thrashing — Wikipedia](https://en.wikipedia.org/wiki/Thrashing_(computer_science))
- [The multi-generational LRU — LWN.net](https://lwn.net/Articles/851184/)
- [Multi-Gen LRU — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/multigen_lru.html)
- [Pressure stall information — Linux kernel docs](https://www.kernel.org/doc/html/latest/accounting/psi.html)
- [Page Frame Reclamation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
