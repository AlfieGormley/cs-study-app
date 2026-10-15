---
id: mem-tlb-coherence
sourceLesson: mem-tlb
title: Address-space tags and shootdowns
level: intermediate
minutes: 3
summary: ASIDs and PCIDs allow cached translations from distinct address spaces to coexist.
---

## Context switches, ASIDs and PCIDs

A TLB entry says "VPN 0x400 maps to PFN 0x9a2". That is only true for one address space. When the kernel switches to another process (by loading CR3), the old entries become wrong.

The traditional x86 approach without PCIDs invalidates relevant non-global translations on an ordinary CR3 write. The new process can then pay refill misses; enabled global translations follow the exception described below.

Two features reduce the damage:

- **Global pages.** With global-page support enabled, translations marked by the **G** bit can survive ordinary CR3 writes. Traditionally shared kernel mappings used this feature to remain cached across switches; explicit invalidation and KPTI policy still matter.
- **Address-space identifiers.** Tags let translations from several address spaces coexist, reducing flushes. Mapping changes and tag reuse still require invalidation. ARM and MIPS call these **ASIDs**. On x86 they are **PCIDs** (process-context identifiers): 12 bits held in the low bits of CR3, allowing 4,096 tag values.

```
 VPN    PFN    PCID
 0x400  0x9a2  3    <- process A
 0x400  0x177  5    <- process B
```

Linux on x86 assigns each CPU a small pool of PCIDs and recycles them across processes rather than giving every process a permanent tag. PCIDs help reduce **KPTI** overhead (the address-space units). When KPTI is active, a userspace system call switches between reduced user and full kernel page-table views. KPTI also works without PCIDs. With PCIDs and appropriate invalidation handling, useful translations from both views may remain cached, reducing refill work. The size of the saving depends on the CPU and workload.

Threads in the same process normally share an address space, so changing thread identity alone does not require switching the userspace page-table root or discarding its translations. Kernel entry/exit, architectural state and security policy can add separate work.

## TLB shootdowns

Each CPU core has its own TLB. Suppose a process has threads on cores 0 to 7 and one thread calls `munmap` (or `mprotect` to remove write access). The kernel updates the page table, but cores 1 to 7 may still hold the old translation.

The kernel must perform a **TLB shootdown**:

1. Update the PTEs.
2. Send an **inter-processor interrupt (IPI)** to every other core that might be running this address space.
3. Each core invalidates the entries (`INVLPG` or a full flush) and acknowledges.
4. The initiating core waits for every acknowledgement before reusing the freed frames.

Shootdown cost varies with hardware, target CPUs and kernel policy. The IPI sequence above is a common implementation, not a requirement that every unmap interrupt every core; deferred invalidation and architectural broadcast mechanisms may differ. Workloads that `mmap` and `munmap` frequently in heavily threaded processes can spend real time here. That is one reason memory allocators avoid returning memory to the OS on every `free`, and why the kernel batches invalidations.

## Key takeaways
- ASIDs and PCIDs allow cached translations from distinct address spaces to coexist.
- Mapping changes still need invalidation, sometimes involving remote CPUs.
- Repeated mapping churn can increase shootdown work.

## Further reading
- [OSTEP: Paging: Faster Translations (TLBs) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Transparent Hugepage Support — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [HugeTLB Pages — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/hugetlbpage.html)
- [Diagnosing latency issues (THP section) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [What Every Programmer Should Know About Memory, Ulrich Drepper (PDF)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
