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

Translation replaces the VPN with the PFN and keeps the offset unchanged. The offset never needs translating because a page and its frame have the same internal layout.

> [!example] A toy translation
> A machine has 16-bit addresses and 4 KiB pages: 4 bits of VPN, 12 bits of offset, so 16 virtual pages. The page table says VPN 3 maps to PFN 7.
>
> Virtual 0x3A7C: VPN = 0x3, offset = 0xA7C. Replace 3 with 7: physical **0x7A7C**.
>
> With 4 KiB pages, the last three hex digits are always the offset, which makes hex translation quick by eye.

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

A single flat array with one PTE per virtual page is simple, but consider its size.

- **32-bit**, 4 KiB pages, 4-byte entries: 2^32 / 2^12 = 2^20 entries × 4 B = **4 MiB per process**. Tolerable, but it adds up across hundreds of processes.
- **48-bit** (x86-64), 4 KiB pages, 8-byte entries: 2^36 entries × 8 B = 2^39 B = **512 GiB** for the full 48-bit space. This is an impractical flat-table overhead for ordinary processes.

Yet a typical process uses only a few hundred MiB scattered across a 128 TiB space. Nearly all of the flat table would say "not present". The fix is to avoid storing those empty stretches.

## Multi-level page tables

The trick is to **page the page table**. Split the VPN into several chunks and build a tree. The top-level table points to second-level tables, and so on. If an entire region is unused, the upper entry is simply marked not-present, and the tables below it are never allocated.

x86-64 uses a 4-level tree for 48-bit addresses. Each table is exactly one 4 KiB page holding 512 entries of 8 bytes, so each level consumes 9 bits of the address (2^9 = 512):

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

The physical address of the top-level table lives in the **CR3** register. A context switch to another process loads its CR3 value, and that one register write switches the whole address space.

### A walk, bit by bit

Translate the virtual address **0x7ffd4a3b2c18** (a typical stack address). First write the 48 bits in binary and cut them into fields:

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

(3,096 is 0xc18.) Now the MMU walks the tree:

```
CR3 -> PML4 table
       entry 255 -> PDPT table
         entry 501 -> PD table
           entry 81 -> PT table
             entry 434 -> PFN 0x1a2b3
physical = (0x1a2b3 << 12) | 0xc18
         = 0x1a2b3c18
```

At each level the hardware reads one 8-byte entry, checks the present and permission bits, and takes the next table's physical address from bits 12 to 51. If any level's entry is not present, the walk stops with a page fault.

> [!warning] Four extra memory reads
> A naive walk costs **four memory accesses** before the real one, a 5× slowdown if every access had to do it. The TLB (next lesson) caches finished translations so that most accesses skip the walk entirely.

### How much space does it save?

Imagine a small process whose code and heap sit in one 2 MiB region near the bottom of the address space and whose stack sits near the top.

- 1 PML4 table (always needed).
- Code and heap: 1 PDPT, 1 PD, 1 PT.
- Stack: a different PML4 entry, so its own PDPT, PD and PT.

That is 7 tables × 4 KiB = **28 KiB** of page tables, against 512 GiB for a flat table. Ignoring kernel mappings, KPTI and other process regions, this toy count assumes the stack also fits within one 2 MiB region. Table cost depends on mapped address distribution as well as size: each fully used PT maps 2 MiB for 4 KiB of table, about 0.2% overhead.

## Huge pages fall out naturally

A PD entry normally points to a PT. If its **PS** (page size) bit is set, it instead points directly to a 2 MiB-aligned 2 MiB frame, and the walk stops one level early. The low **21 bits** of the address become the offset.

Likewise a PDPT entry with PS set maps a **1 GiB** page with a 30-bit offset. Lesson 3 explains why huge pages matter for TLB performance.

## Five-level paging

48 bits gives 256 TiB of virtual space, and the architecture allows up to 52-bit physical addresses (4 PiB). Some very large servers wanted more virtual space, so Intel added **5-level paging** (LA57), available on supporting CPU models.

In five-level mode, PML5 is Linux PGD and PML4 is Linux P4D. In four-level mode P4D is folded and PML4 acts as PGD. 9 × 5 + 12 = **57 bits**, or 128 PiB of virtual space.

Linux supports it when built with the option and run on a capable CPU. To avoid breaking programs that stash tags in the high bits of pointers, Linux hands out addresses above the 47-bit boundary only if a program asks for one explicitly by passing a high hint address to `mmap`.

Five-level paging can add a lookup to an uncached walk. A capable kernel can enable it on supported hardware even for small-memory workloads; unsupported hardware uses the folded four-level configuration.

## Other designs

Not every architecture uses a radix tree:

- **Inverted page tables** keep entries indexed by physical frame, with a lookup mechanism such as a hash index over address-space identity and virtual page number. They are distinct from a hashed forward mapping table; not every architecture using hashed translation has one entry per physical frame.
- ARM64 uses a tree very like x86-64's, with a choice of 4 KiB, 16 KiB or 64 KiB granules. Apple's M-series Macs use 16 KiB pages.

## Trade-offs and pitfalls

- **Internal fragmentation.** Memory is handed out in whole pages. An independently backed 1-byte region can occupy a whole base page once allocated. Average half-page waste assumes roughly uniform allocation remainders; sharing, lazy allocation and suballocation change the result. Bigger pages can increase waste.
- **Page tables cost real memory.** A dense, populated 100 GiB mapping with 4 KiB pages needs about 200 MiB of leaf page tables (100 GiB / 2 MiB per PT × 4 KiB). Many processes sharing a large mapping each pay that separately, which is one reason big databases use huge pages.
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
