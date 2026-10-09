---
id: mem-paging
title: Paging and page tables
level: intermediate
minutes: 14
summary: Pages and frames, what a page table entry holds, translating an address bit by bit, and why x86-64 uses a 4- or 5-level tree of tables.
---

Segmentation chopped memory into variable-sized pieces and paid for it with external fragmentation. **Paging** takes the opposite approach: chop *everything* into small, fixed-size blocks.

- The virtual address space is divided into **pages**.
- Physical memory is divided into **frames** (or page frames) of the same size.
- A **page table** records, for each virtual page, which physical frame holds it.

For a fixed base-page size, any suitable free frame can back a page; an ordinary virtual region need not occupy one physical hole. Physical contiguity still matters for huge pages and some device/kernel allocations. A process's pages can be scattered all over RAM while appearing perfectly contiguous to the program.

On x86-64 the standard page size is **4 KiB** (4,096 bytes), with optional huge pages of 2 MiB and 1 GiB.

## Splitting an address

Since a page is 4,096 = 2^12 bytes, the low 12 bits of an address say where you are *inside* the page. The remaining high bits say *which* page.

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
PA = PFN × P + off
where
P: the page size in bytes; 4 KiB = 4,096 on x86-64
k: the number of offset bits; 12 for 4 KiB pages, because 2^12 = 4,096
2^k: 2 multiplied by itself k times
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

With 4 KiB pages, multiplying or dividing by 2^12 = 0x1000 just moves hex digits, so the last three hex digits are always the offset. That makes hex translation quick by eye: replace the leading digits (the VPN) with the PFN.

Here is the same idea in Python:

```python
PAGE_BITS = 12
OFF_MASK = (1 << PAGE_BITS) - 1
page_table = {0: 5, 1: 9, 3: 7}  # VPN->PFN

def translate(va):
    vpn = va >> PAGE_BITS
    off = va & OFF_MASK
    if vpn not in page_table:
        raise MemoryError("page fault")
    pfn = page_table[vpn]
    return (pfn << PAGE_BITS) | off

print(hex(translate(0x3A7C)))  # 0x7a7c
print(hex(translate(0x0123)))  # 0x5123
translate(0x2000)  # VPN 2: page fault
```

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

The OS sets P, R/W, U/S and NX to express permissions. The CPU maintains **A** and **D** for translation use and writes. After clearing them, the OS must use the required invalidation protocol to observe later accesses reliably; cached translations do not promise a fresh in-memory bit update on every access. The OS reads those bits later to decide what to evict (lesson 5) and whether an evicted page must be written to disk first.

If P is 0, the hardware ignores the rest of the entry and raises a **page fault**. The OS can encode software state such as swap information in a non-present entry, while respecting architectural and security constraints. Non-present entries must not be treated as unconstrained storage on every implementation.

For ordinary user-mode accesses with NX support enabled and coherent translations, writing through R/W=0, reading a supervisor-only mapping, or executing an NX mapping faults. Supervisor write protection depends on control state; cached translations must be invalidated after changing permissions. This is how code is made read-only and data non-executable.

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
2^s: 2 multiplied by itself s times; dividing by it discards the s bits below the field
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

PML4 = 011111111   = 255
PDPT = 111110101   = 501
PD   = 001010001   = 81
PT   = 110110010   = 434
off  = 110000011000 = 0xc18
```

The same split in code:

```python
def split(va):
    off  =  va        & 0xFFF
    pt   = (va >> 12) & 0x1FF
    pd   = (va >> 21) & 0x1FF
    pdpt = (va >> 30) & 0x1FF
    pml4 = (va >> 39) & 0x1FF
    return pml4, pdpt, pd, pt, off

print(split(0x7ffd4a3b2c18))
# (255, 501, 81, 434, 3096)
```

(3,096 is 0xc18. In the code, `va >> s` is the division by 2^s and `& 0x1FF` keeps 9 bits.) Now the MMU walks the tree:

```
CR3 -> PML4 table
       entry 255 -> PDPT table
         entry 501 -> PD table
           entry 81 -> PT table
             entry 434 -> PFN 0x1a2b3
physical = (0x1a2b3 << 12) | 0xc18
         = 0x1a2b3c18
```

The last line is the same frame-plus-offset rule as before, written with a shift (`<<`) and a bitwise OR (`|`):

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
> A naive walk costs **four memory accesses** before the real one, a 5× slowdown if every access had to do it. The TLB (next lesson) caches finished translations so that most accesses skip the walk entirely.

### How much space does it save?

Imagine a small process whose code and heap sit in one 2 MiB region near the bottom of the address space and whose stack sits near the top.

- 1 PML4 table (always needed).
- Code and heap: 1 PDPT, 1 PD, 1 PT.
- Stack: a different PML4 entry, so its own PDPT, PD and PT.

That is 7 tables × 4 KiB = **28 KiB** of page tables, against 512 GiB for a flat table. Ignoring kernel mappings, KPTI and other process regions, this toy count assumes the stack also fits within one 2 MiB region. Table cost depends on mapped address distribution as well as size. For a densely mapped region, the leaf tables dominate:

```formula
S_PT = M / C_PD × 4 KiB
o = 4 KiB / 2 MiB = 4 / 2,048 ≈ 0.2 %
where
S_PT: the memory used by leaf page tables (PTs) for the region
M: the size of the densely mapped region
C_PD: the memory one full PT maps, 2 MiB (512 entries × 4 KiB)
KiB: kibibyte, 1,024 bytes; each PT is one 4 KiB page
MiB: mebibyte, 1,024 KiB
o: the overhead: page-table bytes per mapped byte
≈: approximately equal to
%: per cent, hundredths
In words: every 2 MiB of densely mapped memory needs one 4 KiB leaf table, about 0.2 % extra; the upper levels add a little more.
```

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

Likewise a PDPT entry with PS set maps a **1 GiB** page with a 30-bit offset. Lesson 3 explains why huge pages matter for TLB performance.

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
- ARM64 uses a tree very like x86-64's, with a choice of 4 KiB, 16 KiB or 64 KiB granules. Apple's M-series Macs use 16 KiB pages.

## Trade-offs and pitfalls

- **Internal fragmentation.** Memory is handed out in whole pages. An independently backed 1-byte region can occupy a whole base page once allocated. Average half-page waste assumes roughly uniform allocation remainders; sharing, lazy allocation and suballocation change the result. Bigger pages can increase waste.
- **Page tables cost real memory.** A dense, populated 100 GiB mapping with 4 KiB pages needs 51,200 leaf page tables (100 GiB divided by the 2 MiB each one maps), and 51,200 × 4 KiB is about 200 MiB. Many processes sharing a large mapping each pay that separately, which is one reason big databases use huge pages.
- **Don't confuse page-aligned with frame-contiguous.** Two adjacent virtual pages can be in frames gigabytes apart. DMA mappings must meet the device's requirements; options include scatter/gather lists, IOMMU translation or physically contiguous buffers.

## Key takeaways
- Paging removes the requirement that an ordinary virtual region fit one physical hole; huge and contiguous allocations can still suffer fragmentation.
- An address splits into a page number and an offset; translation swaps the page number for a frame number and keeps the offset.
- PTEs carry permission bits (present, writable, user, no-execute) and hardware-maintained accessed and dirty bits.
- A flat page table for 48-bit addresses would be 512 GiB; x86-64 uses a 4-level tree of 512-entry tables indexed by 9 bits each, rooted at CR3.
- A PS bit at the PD or PDPT level makes a 2 MiB or 1 GiB huge page; 5-level paging extends addresses to 57 bits.
- A full walk costs four memory reads, which is why the TLB exists.

## Further reading
- [OSTEP: Paging: Introduction (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)
- [OSTEP: Paging: Smaller Tables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-smalltables.pdf)
- [Page tables — Linux kernel documentation](https://www.kernel.org/doc/html/latest/mm/page_tables.html)
- [x86_64 memory map — Linux kernel documentation](https://www.kernel.org/doc/html/latest/arch/x86/x86_64/mm.html)
- [Five-level page tables — LWN.net](https://lwn.net/Articles/717293/)
- [Intel 5-level paging — Wikipedia](https://en.wikipedia.org/wiki/Intel_5-level_paging)
- [Page table — Wikipedia](https://en.wikipedia.org/wiki/Page_table)
