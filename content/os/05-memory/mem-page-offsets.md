---
id: mem-page-offsets
sourceLesson: mem-paging
title: Pages, frames and unchanged offsets
level: intermediate
minutes: 5
summary: Translation replaces a virtual page number with a frame number and preserves the offset.
---

Segmentation chopped memory into variable-sized pieces and paid for it with external fragmentation. **Paging** takes the opposite approach: chop *everything* into small, fixed-size blocks.

- The virtual address space is divided into **pages**.
- Physical memory is divided into **frames** (or page frames) of the same size.
- A **page table** records, for each virtual page, which physical frame holds it.

For a fixed base-page size, any suitable free frame can back a page; an ordinary virtual region need not occupy one physical hole. Physical contiguity still matters for huge pages and some device/kernel allocations. A process's pages can be scattered all over RAM while appearing perfectly contiguous to the program.

On x86-64 the standard page size is **4 KiB** (4,096 bytes), with optional huge pages of 2 MiB and 1 GiB.

## Splitting an address

Since a 4 KiB page contains 4,096 bytes, the low 12 bits of an address say where you are *inside* the page. The remaining high bits say *which* page.

```
 virtual address
 +------------------+------------+
 | virtual page no. |  offset    |
 |      (VPN)       |  12 bits   |
 +------------------+------------+
          | page table lookup
          v
 +------------------+------------+
 |  frame no. (PFN) |  offset    |
 +------------------+------------+
 physical address
```

Translation replaces the VPN with the PFN and keeps the offset unchanged. The offset never needs translating because a page and its frame have the same internal layout. As arithmetic, splitting is a division: the quotient is the page number and the remainder is the offset.

```formula
P = 2^k
VPN = ⌊VA / P⌋
off = VA mod P
PA = PFN P + off
where
P: the page size in bytes; 4 KiB = 4,096 on x86-64
k: the number of offset bits; 12 for 4 KiB pages, because 2^12 = 4,096
2^k: k copies of 2 multiplied together
VA: the virtual address
VPN: the virtual page number: which page the address falls in
off: the offset: how far into the page, from 0 to P − 1
⌊ ⌋: floor: round down to a whole number
mod: the remainder after division; for example 13 mod 5 = 3
PA: the physical address
PFN: the physical frame number: which frame holds the page, read from the page table entry for VPN
In words: divide the address by the page size; the quotient picks the page and the remainder is the position inside it. Translation swaps the page number for a frame number and keeps the remainder.
```

Because P is a power of two, the division needs no divider. The offset is simply the low k bits and the VPN is the bits above them, which is why the code below uses shifts (`>>`) and masks (`&`) instead.

> [!example] A toy translation
> A machine has 16-bit addresses and 4 KiB pages: 4 bits of VPN, 12 bits of offset, so 16 virtual pages. The page table says VPN 3 maps to PFN 7.

```formula
VPN = ⌊0x3A7C / 2^12⌋ = 0x3
off = 0x3A7C mod 2^12 = 0xA7C
PA = 0x7 × 2^12 + 0xA7C = 0x7A7C
where
VPN: the virtual page number; 0x3 maps to frame 0x7 in this page table
off: the offset inside the page
2^12: 4,096, which is 0x1000 in hexadecimal: one 4 KiB page
⌊ ⌋: floor: round down to a whole number
mod: the remainder after division
PA: the physical address
In words: 0x3A7C is 0xA7C bytes into page 3; page 3 lives in frame 7, so the byte is 0xA7C bytes into frame 7, at 0x7A7C.
```

With 4 KiB pages, multiplying or dividing by 4,096 (0x1000) moves hex digits, so the last three hex digits are always the offset. That makes hex translation quick by eye: replace the leading digits (the VPN) with the PFN.

Here is the same idea in Python:

```python
PAGE_BITS = 12
OFF_MASK = (1 << PAGE_BITS) - 1
# Sparse toy mappings: VPN to frame number.
page_table = {0: 5, 1: 9, 3: 7}

def translate(va):
    # High bits pick the page-table entry.
    vpn = va >> PAGE_BITS
    # The low offset bits stay unchanged.
    off = va & OFF_MASK
    if vpn not in page_table:
        raise MemoryError("page fault")
    pfn = page_table[vpn]
    # Place the frame above the offset bits.
    return (pfn << PAGE_BITS) | off

print(hex(translate(0x3A7C)))  # 0x7a7c
print(hex(translate(0x0123)))  # 0x5123
translate(0x2000)  # VPN 2: page fault
```

## Key takeaways
- Translation replaces a virtual page number with a frame number and preserves the offset.
- A power-of-two page size lets shifts and masks separate the fields.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
