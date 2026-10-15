---
id: mem-swap-backing
sourceLesson: mem-page-faults
title: Reclaiming file and anonymous backing
level: intermediate
minutes: 3
summary: Clean file backing can be reread; preserving live anonymous contents during reclaim normally needs swap.
---

## Swap

When RAM runs short, the kernel must free frames (the replacement units covers how it chooses). What it does depends on the page:

| Page kind | To reclaim it |
|---|---|
| Clean file page | Just drop it; reread later |
| Dirty file page | Write it back to the file |
| Anonymous page | Write it to **swap** |

Preserving live anonymous data during reclaim normally requires swap backing. This is different from freeing or explicitly discarding unneeded anonymous pages, which can happen without swap. With swap, it writes the page out and stores a **swap entry** (which swap device, which slot) in the now not-present PTE. The OS is allowed to use those bits because the hardware ignores a PTE whose present bit is clear. A later access resolves the swap entry. It can use resident swap-cache or compressed backing; a storage read is not inevitable.

`vm.swappiness` (default 60, range 0 to 200) tells the kernel how willing it is to swap anonymous pages compared with dropping page cache.

Modern variants compress instead of writing to disk:

- **zswap**: a compressed RAM cache in front of a swap device.
- **zram**: a compressed RAM block device used as swap. Several operating-system distributions use it; exact defaults depend on version and configuration. Optional zram writeback can use a backing device.

Compression trades CPU and metadata for saved backing capacity; cost and compression ratio depend on data and configuration.

## Other uses of the fault path

- **Stack growth**: eligible grow-down stack mappings may expand within limits; an arbitrary below-stack fault does not guarantee expansion.
- **Guard pages**: deliberately unmapped pages below thread stacks turn overflows into immediate `SIGSEGV`.
- **userfaultfd**: lets a user-space program handle faults on a region. QEMU uses it for post-copy live migration, fetching guest pages over the network on demand.
- **Garbage collectors and databases** use `mprotect` to trap writes and record which pages are dirty.

## Key takeaways
- Clean file backing can be reread; preserving live anonymous contents during reclaim normally needs swap.
- Swap backing may be cached or compressed, so swap-in need not read a storage device.
- Fault machinery also supports guarded stacks, userfaultfd and write tracking.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
