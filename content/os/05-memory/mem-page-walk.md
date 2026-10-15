---
id: mem-page-walk
sourceLesson: mem-paging
title: Walking an x86 address bit by bit
level: intermediate
minutes: 4
summary: Extract one index per level, then combine the final frame with the unchanged offset.
---

### A walk, bit by bit

Translate the virtual address **0x7ffd4a3b2c18** (a typical stack address). Each table index is a 9-bit field, found by shifting the address right past everything below the field (dividing by a power of two) and keeping 9 bits (the remainder after dividing by 512):

```formula
i = ⌊VA / 2^s⌋ mod 512
i_PML4 = ⌊VA / 2^39⌋ mod 512 = 255
i_PDPT = ⌊VA / 2^30⌋ mod 512 = 501
i_PD = ⌊VA / 2^21⌋ mod 512 = 81
i_PT = ⌊VA / 2^12⌋ mod 512 = 434
off = VA mod 2^12 = 0xc18 = 3,096
where
i: the index into one level's table, from 0 to 511
VA: the virtual address, here 0x7ffd4a3b2c18
s: the bit position where that level's field starts: 39, 30, 21 or 12
2^s: s copies of 2 multiplied together; dividing by it discards the s bits below the field
⌊ ⌋: floor: round down to a whole number
mod: the remainder after division; mod 512 keeps the lowest 9 bits, because 512 = 2^9
i_PML4: the index into the top-level PML4 table
i_PDPT: the index into the PDPT
i_PD: the index into the PD
i_PT: the index into the PT
off: the 12-bit offset inside the final 4 KiB page
In words: cut the 48 bits into four 9-bit table indices and a 12-bit offset; these are the numbers the MMU uses at each level.
```

By hand, write the 48 bits in binary and cut them into fields:

```
0x7ffd4a3b2c18 =
011111111 111110101 001010001
110110010 110000011000

PML4: 011111111   (255)
PDPT: 111110101   (501)
PD:   001010001   (81)
PT:   110110010   (434)
off:  110000011000 (0xc18)
```

The same split in code:

```python
def split(va):
    # Keep the offset, then extract 9-bit
    # indices from leaf towards root.
    off  =  va        & 0xFFF
    pt   = (va >> 12) & 0x1FF
    pd   = (va >> 21) & 0x1FF
    pdpt = (va >> 30) & 0x1FF
    pml4 = (va >> 39) & 0x1FF
    return pml4, pdpt, pd, pt, off

print(split(0x7ffd4a3b2c18))
# (255, 501, 81, 434, 3096)
```

(3,096 is hexadecimal 0xc18. In the code, `va >> s` discards the low bits selected by the shift amount and `& 0x1FF` keeps the next nine bits.) Now the MMU walks the tree:

```
CR3 -> PML4 table
       entry 255 -> PDPT table
         entry 501 -> PD table
           entry 81 -> PT table
             entry 434 -> PFN 0x1a2b3
```

After the walk, combine the final frame and offset using the same rule as before:

```formula
PA = PFN × 2^12 + off
PA = 0x1a2b3 × 0x1000 + 0xc18
PA = 0x1a2b3c18
where
PA: the physical address
PFN: the physical frame number from the PT entry; here 0x1a2b3
2^12: 4,096 (0x1000), the page size; multiplying by it appends three hex zeros
off: the offset inside the page; here 0xc18
In words: the frame number supplies everything above the low 12 bits, and the unchanged offset fills the low 12 bits.
```

At each level the hardware reads one 8-byte entry, checks the present and permission bits, and takes the next table's physical address from bits 12 to 51. If any level's entry is not present, the walk stops with a page fault.

> [!warning] Four extra memory reads
> A naive walk costs **four memory accesses** before the real one, five total reads per data access in a serial, equally costly read model. This is a read-count model, not a universal latency multiplier. The TLB (next lesson) caches finished translations so that most accesses skip the walk entirely.

## Key takeaways
- Extract one index per level, then combine the final frame with the unchanged offset.
- An uncached four-level walk reads four entries before accessing the data.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
