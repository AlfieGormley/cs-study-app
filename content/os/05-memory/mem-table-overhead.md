---
id: mem-table-overhead
sourceLesson: mem-paging
title: Counting table pages and fragmentation
level: intermediate
minutes: 3
summary: Table cost depends on the distribution and density of populated addresses.
---

### How much space does it save?

Imagine a small process whose code and heap sit in one 2 MiB region near the bottom of the address space and whose stack sits near the top.

- 1 PML4 table (always needed).
- Code and heap: 1 PDPT, 1 PD, 1 PT.
- Stack: a different PML4 entry, so its own PDPT, PD and PT.

That is 7 tables × 4 KiB = **28 KiB** of page tables, against 512 GiB for a flat table. Ignoring kernel mappings, KPTI and other process regions, this toy count assumes the stack also fits within one 2 MiB region. Table cost depends on mapped address distribution as well as size. For a densely mapped region, the leaf tables dominate:

```formula
S_PT = ⌈M / C_PD⌉ × 4 KiB
o = 4 KiB / 2 MiB = 4 / 2,048 ≈ 0.2 %
where
S_PT: the memory used by leaf page tables (PTs) for the region
M: the size of a densely mapped region beginning on a 2 MiB boundary
⌈ ⌉: ceiling: round up so a partly used leaf table still occupies a whole table page
C_PD: the memory one full PT maps, 2 MiB (512 entries × 4 KiB)
KiB: kibibyte, 1,024 bytes; each PT is one 4 KiB page
MiB: mebibyte, 1,024 KiB
o: the overhead: page-table bytes per mapped byte
≈: approximately equal to
%: per cent, hundredths
In words: every 2 MiB of densely mapped memory needs one 4 KiB leaf table, about 0.2 % extra; the upper levels add a little more.
```

## Trade-offs and pitfalls

- **Internal fragmentation.** Memory is handed out in whole pages. An independently backed 1-byte region can occupy a whole base page once allocated. Average half-page waste assumes roughly uniform allocation remainders; sharing, lazy allocation and suballocation change the result. Bigger pages can increase waste.
- **Page tables cost real memory.** A dense, populated 100 GiB mapping with 4 KiB pages needs 51,200 leaf page tables (100 GiB divided by the 2 MiB each one maps), and 51,200 × 4 KiB is about 200 MiB. Many processes sharing a large mapping each pay that separately, which is one reason big databases use huge pages.
- **Don't confuse page-aligned with frame-contiguous.** Two adjacent virtual pages can be in frames gigabytes apart. DMA mappings must meet the device's requirements; options include scatter/gather lists, IOMMU translation or physically contiguous buffers.

## Key takeaways
- Table cost depends on the distribution and density of populated addresses.
- Dense mappings pay mostly for leaf tables, while isolated regions need separate upper paths.
- Virtual alignment does not guarantee physical contiguity.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
