---
id: mem-fault-handler
sourceLesson: mem-page-faults
title: From a hardware fault to a VMA decision
level: intermediate
minutes: 3
summary: The x86 fault record supplies the address and access type so a resolved instruction can restart.
---

The earlier paging units treated a not-present page table entry as an error. In practice it is the opposite. The **page fault** is the most useful exception the hardware has, and Linux leans on it for almost everything clever about memory.

The idea is simple. The OS deliberately leaves PTEs not-present, or present but read-only, and waits. When the program touches the page, the CPU traps into the kernel, which decides what the page *should* be, fixes the PTE and lets the instruction run again. On successful resolution the instruction resumes; the program can still observe latency and fault counters, and some faults fail.

That one trick gives you:

- **Demand paging**: memory is allocated only when first touched.
- **Copy-on-write**: `fork` shares pages until one side writes.
- **Memory-mapped files**: file contents appear in memory and load lazily.
- **Swap**: pages can live on disk and come back on demand.

## What the hardware does

On x86-64, when the MMU cannot complete a translation (a not-present entry at any level) or the access breaks a permission bit, it raises exception 14, the **page fault (#PF)**. Before jumping to the kernel's handler it:

1. Puts the faulting virtual address in the **CR2** register.
2. Pushes a **page-fault error code** describing the access.
3. Saves the instruction pointer of the faulting instruction, not the next one, so the instruction can be **restarted**.

| Error bit | Set means |
|---|---|
| P (0) | Page present: a protection violation |
| W (1) | The access was a write |
| U (2) | It came from user mode |
| I (4) | It was an instruction fetch |

So the kernel learns exactly what happened: "user-mode write to 0x7f3a1000, page not present".

## What Linux does with it

The handler (`exc_page_fault`, then `handle_mm_fault`) asks one question first: **is this address inside a VMA?**

A **VMA** (virtual memory area) is the kernel's record of one mapped region: start, end, permissions and what backs it (a file, or nothing for anonymous memory). You can see them in `/proc/<pid>/maps`.

```
fault at addr, access type
        |
  addr in a VMA? -- no --> SIGSEGV
        | yes
  access allowed --- no --> SIGSEGV
  by VMA perms?
        | yes
  what is the page?
   - never touched -> allocate frame
   - in page cache -> map it
   - in swap       -> read it back
   - COW-shared    -> copy it
        |
  fix PTE, return, retry instruction
```

The crucial distinction is between the **page table** (what the hardware sees right now) and the **VMA** (what the process is allowed to have). Missing or incompatible VMAs are common SIGSEGV causes, but the VMA check is not the whole story. File faults can deliver SIGBUS; allocation can fail; architecture-specific protection and special mappings have additional rules.

## Key takeaways
- The x86 fault record supplies the address and access type so a resolved instruction can restart.
- Linux compares the access with mapping policy and backing state, rather than treating every missing PTE as an error.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
