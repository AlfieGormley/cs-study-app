---
id: mem-page-table-tree
sourceLesson: mem-paging
title: Building a sparse page-table tree
level: intermediate
minutes: 4
summary: A sparse tree avoids allocating lower tables for entirely unused regions.
---

## Multi-level page tables

The trick is to **page the page table**. Split the VPN into several chunks and build a tree. The top-level table points to second-level tables, and so on. If an entire region is unused, the upper entry is simply marked not-present, and the tables below it are never allocated.

x86-64 uses a 4-level tree for 48-bit addresses. Each table is exactly one 4 KiB page holding 512 entries of 8 bytes, so each level consumes 9 bits of the address. The general rule for how many levels a tree needs:

```formula
e = P / s_PTE
b = log_2(e)
L = ⌈(n − k) / b⌉
e = 4,096 B / 8 B = 512
b = log_2(512) = 9
L = ⌈(48 − 12) / 9⌉ = 4
where
e: the number of entries in one table, when each table fills exactly one page
P: the page size; 4,096 bytes here
s_PTE: the size of one entry; 8 bytes on x86-64
b: the address bits each level consumes: the bits needed to pick one of e entries
log_2: the base-2 logarithm: the power you raise 2 to in order to get the number; 2^9 = 512, so log_2(512) = 9
L: the number of levels in the tree
n: the number of virtual-address bits translated; 48 here
k: the number of offset bits; 12 for 4 KiB pages
⌈ ⌉: ceiling: round up to a whole number (a part-used level is still a level)
B: bytes
In words: a page-sized table of 8-byte entries holds 512 of them, so each level picks one of 512 using 9 bits, and the 36 page-number bits need 4 levels.
```

The 48 bits split like this:

```
47   39 38   30 29   21 20   12 11     0
+------+------+------+------+--------+
| PML4 | PDPT |  PD  |  PT  | offset |
|  9   |  9   |  9   |  9   |   12   |
+------+------+------+------+--------+
```

9 + 9 + 9 + 9 + 12 = 48 bits. Bits 63 to 48 must be copies of bit 47 (the canonical-address rule).

| Intel name | Linux name | One entry covers |
|---|---|---|
| PML4 | PGD (P4D folded) | 512 GiB |
| PDPT | PUD | 1 GiB |
| PD | PMD | 2 MiB |
| PT | PTE | 4 KiB |

Each level up multiplies the coverage by 512, because one entry points at a whole table of 512 entries below it:

```formula
C_PT = 4 KiB
C_PD = 512 × 4 KiB = 2 MiB
C_PDPT = 512 × 2 MiB = 1 GiB
C_PML4 = 512 × 1 GiB = 512 GiB
where
C_PT: the memory one PT entry maps: one 4 KiB page
C_PD: the memory one PD entry covers: a whole PT's worth of pages
C_PDPT: the memory one PDPT entry covers
C_PML4: the memory one PML4 entry covers
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024 KiB
GiB: gibibyte, 1,024 MiB
In words: 512 × 4 KiB is 2 MiB, 512 × 2 MiB is 1 GiB, and 512 × 1 GiB is 512 GiB, so one top-level entry spans half a tebibyte.
```

The physical address of the top-level table lives in the **CR3** register. A context switch to another process loads its CR3 value, and that one register write switches the whole address space.

## Key takeaways
- A sparse tree avoids allocating lower tables for entirely unused regions.
- Four 9-bit indices and a 12-bit offset cover a 48-bit address.
- CR3 identifies the active x86 page-table root.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
