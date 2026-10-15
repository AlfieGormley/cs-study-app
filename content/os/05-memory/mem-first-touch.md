---
id: mem-first-touch
sourceLesson: mem-page-faults
title: Demand-zero memory and first-touch faults
level: intermediate
minutes: 3
summary: A virtual reservation can precede physical allocation.
---

## Demand paging in action

A large glibc allocation may use anonymous mmap, depending on allocator state and tunables. An ordinary new anonymous mapping without prefaulting can initially reserve a virtual region with backing populated lazily. Under a base-page model, first writes allocate zero-filled backing; page size, THP and prior population affect the fault count.

This C program counts those faults:

```c
#include <stdio.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>

static long minflt(void) {
    struct rusage u;
    getrusage(RUSAGE_SELF, &u);
    return u.ru_minflt;
}

int main(void) {
    size_t len = 64UL << 20; /* 64 MiB */
    char *p = mmap(NULL, len,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }
    long step = sysconf(_SC_PAGESIZE);
    if (step <= 0) return 1;
    /* Compare before/after first writes,
       not virtual reservation alone. */
    long before = minflt();
    /* Volatile stores force one touched
       byte per reported base-page size. */
    for (size_t i = 0; i < len; i += step)
        ((volatile char *)p)[i] = 1;
    printf("%ld faults\n",
           minflt() - before);
    munmap(p, len);
}
```

The expected count is the region size divided by the page size, since each page faults once on its first write:

```formula
F = S / P
F = 64 MiB / 4 KiB = 2^26 B / 2^12 B = 2^14
F = 16,384
F_huge = 64 MiB / 2 MiB = 32
where
F: the number of first-touch faults with base pages
S: the size of the region, 64 MiB = 2^26 bytes
P: the page size, 4 KiB = 2^12 bytes
F_huge: the count if every fault mapped a whole 2 MiB huge page
MiB: mebibyte, 2^20 bytes
KiB: kibibyte, 2^10 bytes
B: bytes
In words: one fault per page touched; bigger pages mean proportionally fewer faults.
```

Under the one-fault-per-4-KiB-page model it would report about **16,384** faults. If every fault installs 2 MiB backing, the model gives **32**. Actual output can differ because of multi-size THP, prior population, other process activity and emulation or accounting details; `always` does not guarantee that every fault installs a 2 MiB page.

Two refinements:

- On common Linux configurations, reads of untouched anonymous mappings can use read-only shared zero backing. Architecture, THP and mapping flags affect this; page tables and metadata still cost memory, and calloc may have allocator-specific behavior.
- `MAP_POPULATE` requests prefaulting but does not guarantee full population or future residency. Successful ordinary `mlock` keeps the range resident, whereas `mlock2(MLOCK_ONFAULT)` is lazy. Neither removes every later COW/protection fault, especially across fork.

## Key takeaways
- A virtual reservation can precede physical allocation.
- First-write counts depend on the page size and actual fault/population policy.
- Untouched reads can use shared zero backing on common Linux paths.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
