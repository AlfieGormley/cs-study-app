---
id: mem-copy-on-write
sourceLesson: mem-page-faults
title: Sharing until a private write
level: intermediate
minutes: 3
summary: Fork shares eligible private backing and protects it until a write requires separation.
---

## Copy-on-write and fork

The baseline below uses ordinary 4 KiB private pages. Huge pages, pinned pages and special mappings can follow different paths.

`fork` must give the child a copy of the parent's whole address space. Copying gigabytes would make `fork` unusably slow, especially since most children immediately call `exec` and throw the copy away.

Instead Linux:

1. Creates the child's memory context and mappings, respecting exceptions such as DONTFORK/WIPEONFORK.
2. Shares eligible private backing under COW and write-protects the required mappings; some page-table work can be deferred.
3. Leaves shared mappings shared. Certain private pages, such as pinned pages, may need special copying rather than ordinary COW.

When either process writes, the read-only PTE causes a protection fault. The kernel sees the VMA is writable, so this is a **COW fault**: it allocates a new frame, copies the 4 KiB, points the writer's PTE at the copy with write permission, and drops the reference on the original. If the writer turns out to be the only remaining user, it simply makes the page writable again with no copy.

```
after fork         after child writes
parent  child      parent      child
  \      /            |           |
 [frame 7 RO]    [frame 7]   [frame 9 RW]
                              (copy of 7)
```

Real systems depend on this:

- **Redis** `BGSAVE` forks, and the child writes a snapshot of the frozen dataset while the parent keeps serving. COW can add backing for modified pages, alongside child buffers, new parent allocations and page tables. A write-heavy workload can substantially increase total physical memory use, which is why Redis warns about memory headroom.
- **Pre-fork servers** (Gunicorn, PHP-FPM, Android's Zygote) load code once and fork workers that share it.

> [!warning] COW is not free
> `fork` still copies page tables, so forking a process with 100 GiB mapped takes noticeable time even before any page is copied. Later writes may copy backing or reuse it when exclusive. Suitable posix_spawn implementations can avoid copying the parent's address space for exec; vfork has strict child-side restrictions and is not a drop-in fork replacement.

## Key takeaways
- Fork shares eligible private backing and protects it until a write requires separation.
- A write can copy backing or reuse it when exclusive; page size and state affect the work.
- Fork and later COW need time and memory headroom.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
