---
id: mem-large-page-mappings
sourceLesson: mem-paging
title: Huge pages and wider address spaces
level: intermediate
minutes: 4
summary: A huge-page entry ends the walk early and uses a larger offset.
---

## Huge pages fall out naturally

A PD entry normally points to a PT. If its **PS** (page size) bit is set, it instead points directly to a 2 MiB-aligned 2 MiB frame, and the walk stops one level early. The low **21 bits** of the address become the offset (the 9 PT-index bits plus the 12 ordinary offset bits):

```formula
off = VA mod 2^21
PA = F + off
where
off: the offset inside the 2 MiB page, from 0 to 2^21 − 1
VA: the virtual address
mod: the remainder after division; mod 2^21 keeps the low 21 bits
2^21: 2,097,152 bytes, which is 2 MiB (0x200000)
PA: the physical address
F: the physical start address of the 2 MiB frame, taken from the PD entry; always a multiple of 2 MiB
In words: with a 2 MiB page, everything below bit 21 is offset, and it is added to the start of the 2 MiB frame.
```

For example, VA 0x7f0012345678 in a page whose frame starts at 0x40000000: the low 21 bits are 0x145678, so the physical address is 0x40145678.

Likewise a PDPT entry with PS set maps a **1 GiB** page with a 30-bit offset. The TLB units explain why huge pages matter for TLB performance.

## Five-level paging

48 bits gives 256 TiB of virtual space, and the architecture allows up to 52-bit physical addresses (4 PiB). Some very large servers wanted more virtual space, so Intel added **5-level paging** (LA57), available on supporting CPU models.

In five-level mode, PML5 is Linux PGD and PML4 is Linux P4D. In four-level mode P4D is folded and PML4 acts as PGD. Each extra level adds 9 address bits:

```formula
n = 9 × L + 12
n = 9 × 4 + 12 = 48
n = 9 × 5 + 12 = 57
2^48 B = 256 TiB
2^57 B = 128 PiB
where
n: the number of virtual-address bits translated
L: the number of page-table levels
B: bytes
TiB: tebibyte, 2^40 bytes
PiB: pebibyte, 2^50 bytes (1,024 TiB)
In words: four levels of 9 bits plus a 12-bit offset give 48 bits (256 TiB); a fifth level gives 57 bits (128 PiB), 512 times as much.
```

Linux supports it when built with the option and run on a capable CPU. To avoid breaking programs that stash tags in the high bits of pointers, Linux hands out addresses above the 47-bit boundary only if a program asks for one explicitly by passing a high hint address to `mmap`.

Five-level paging can add a lookup to an uncached walk. A capable kernel can enable it on supported hardware even for small-memory workloads; unsupported hardware uses the folded four-level configuration.

## Other designs

Not every architecture uses a radix tree:

- **Inverted page tables** keep entries indexed by physical frame, with a lookup mechanism such as a hash index over address-space identity and virtual page number. They are distinct from a hashed forward mapping table; not every architecture using hashed translation has one entry per physical frame.
- ARM64 uses a tree very like x86-64's, with a choice of 4 KiB, 16 KiB or 64 KiB granules. macOS on Apple silicon commonly uses 16 KiB pages; fetch the running system’s page size instead of hardcoding this value.

## Key takeaways
- A huge-page entry ends the walk early and uses a larger offset.
- A fifth x86 level adds nine address bits, subject to hardware and kernel support.
- Other architectures choose different granules and translation structures.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
