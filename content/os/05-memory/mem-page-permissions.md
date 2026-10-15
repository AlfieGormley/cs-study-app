---
id: mem-page-permissions
sourceLesson: mem-paging
title: What page-table permission bits mean
level: intermediate
minutes: 2
summary: Page-table entries hold permissions and access state as well as a frame address.
---

## What a page table entry holds

A **page table entry (PTE)** is more than a frame number. For ordinary x86-64 4 KiB leaf mappings, entries are 8 bytes. The table summarizes selected fields; implemented physical-address width and enabled CPU features constrain their interpretation:

| Bit(s) | Name | Meaning |
|---|---|---|
| 0 | P | Present: mapping valid |
| 1 | R/W | Writable |
| 2 | U/S | User mode may access |
| 5 | A | Accessed (set by CPU) |
| 6 | D | Dirty: page written |
| 8 | G | Global translation when enabled |
| 12–51 | PFN field | Address bits, limited by MAXPHYADDR |
| 63 | NX | No-execute |

The OS sets P, R/W, U/S and NX to express permissions. The CPU maintains **A** and **D** for translation use and writes. After clearing them, the OS must use the required invalidation protocol to observe later accesses reliably; cached translations do not promise a fresh in-memory bit update on every access. The OS reads those bits later to decide what to evict (the replacement units) and whether an evicted page must be written to disk first.

If P is 0, the hardware ignores the rest of the entry and raises a **page fault**. The OS can encode software state such as swap information in a non-present entry, while respecting architectural and security constraints. Non-present entries must not be treated as unconstrained storage on every implementation.

For ordinary user-mode accesses with NX support enabled and coherent translations, writing through a read-only mapping, reading a supervisor-only mapping, or executing an NX mapping faults. Supervisor write protection depends on control state; cached translations must be invalidated after changing permissions. This is how code is made read-only and data non-executable.

## Key takeaways
- Page-table entries hold permissions and access state as well as a frame address.
- Hardware permissions require coherent invalidation when software changes a mapping.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
