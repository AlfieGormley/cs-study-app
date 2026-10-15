---
id: mem-flat-table-cost
sourceLesson: mem-paging
title: Why a flat page table is too large
level: intermediate
minutes: 3
summary: A flat table needs an entry for every possible virtual page, including unused pages.
---

## The size problem

A single flat array with one PTE per virtual page is simple, but consider its size. It needs one entry for every page the address space could hold, used or not:

```formula
E = 2^n / P
S = E × s_PTE
where
E: the number of entries in the flat table: one per virtual page
n: the number of virtual-address bits
2^n: the size of the virtual address space in bytes
P: the page size in bytes; 2^12 = 4,096 for 4 KiB pages
S: the size of the flat page table, per process, in bytes
s_PTE: the size of one page table entry (PTE) in bytes: 4 on 32-bit x86, 8 on x86-64
In words: count the pages in the address space, then multiply by the size of one entry.
```

Two cases with 4 KiB pages:

```formula
E_32 = 2^32 / 2^12 = 2^20
S_32 = 2^20 × 4 B = 2^22 B = 4 MiB
E_48 = 2^48 / 2^12 = 2^36
S_48 = 2^36 × 8 B = 2^39 B = 512 GiB
where
E_32: entries for a 32-bit address space (about a million)
S_32: its flat-table size, with 4-byte entries
E_48: entries for a 48-bit address space (x86-64)
S_48: its flat-table size, with 8-byte entries
B: bytes
MiB: mebibyte, 2^20 bytes
GiB: gibibyte, 2^30 bytes
In words: dividing powers of two subtracts exponents and multiplying adds them; a flat table costs 4 MiB per process at 32 bits but 512 GiB at 48 bits.
```

- **32-bit**: **4 MiB per process**. Tolerable, but it adds up across hundreds of processes.
- **48-bit** (x86-64): **512 GiB** for the full 48-bit space. This is an impractical flat-table overhead for ordinary processes.

Yet a typical process uses only a few hundred MiB scattered across a 128 TiB space. Nearly all of the flat table would say "not present". The fix is to avoid storing those empty stretches.

## Key takeaways
- A flat table needs an entry for every possible virtual page, including unused pages.
- Address width, page size and entry size determine that overhead.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
