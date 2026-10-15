---
id: mem-segment-translation
sourceLesson: mem-address-spaces
title: Segments, sharing and fragmented holes
level: basic
minutes: 4
summary: Segment bits select a base and a limit; the remaining bits select an offset.
---

## Segmentation

**Segmentation** generalises base and bounds: instead of one pair per process, there is one pair per logical **segment** (code, heap, stack and so on). Each segment can be placed anywhere in RAM independently, and the gap between heap and stack costs nothing.

The hardware needs to know which segment an address belongs to. One classic approach uses the top bits of the virtual address as a segment number and the rest as an offset (how far into the segment). With a 12-bit offset:

```formula
seg = ⌊VA / 2^12⌋
off = VA mod 2^12
PA = base_seg + off   for off < size_seg
where
VA: the virtual address the program used
seg: the segment number, which is the top bits of VA
off: the offset inside the segment, which is the low 12 bits of VA
2^12: 4,096 (0x1000 in hexadecimal); dividing by it strips off the 12 offset bits
⌊ ⌋: floor: round down to a whole number
mod: the remainder after division; for example 13 mod 5 = 3
base_seg: the base of segment number seg: where it starts in physical memory, read from the segment table
size_seg: the size of segment number seg in bytes, also from the segment table
PA: the physical address
In words: the top bits choose a row of the segment table, the low bits say how far into that segment, and the hardware adds the offset to that row's base after checking that it fits inside the segment.
```

> [!example] Segment translation
> A toy machine has 14-bit virtual addresses. The top 2 bits pick the segment and the low 12 bits are the offset.
>
> | Seg | Name | Base | Size |
> |---|---|---|---|
> | 00 | code | 0x8000 | 2 KiB |
> | 01 | heap | 0xA000 | 3 KiB |
>
> Virtual 0x1068 is `01 0000 0110 1000` in binary: segment 01 (heap), offset 0x068 (104).

In hexadecimal, division by 4,096 (0x1000) drops the last three digits, so the segment and offset can be read off by eye:

```formula
seg = ⌊0x1068 / 2^12⌋ = 1
off = 0x1068 mod 2^12 = 0x068 = 104
off = 104 < 3,072 = size_1
PA = base_1 + off = 0xA000 + 0x068
PA = 0xA068
where
seg: the segment number; 1 (binary 01) is the heap
off: the offset inside the segment, in bytes
2^12: 4,096 (0x1000)
⌊ ⌋: floor: round down to a whole number
mod: the remainder after division
size_1: the heap segment's size, 3 KiB = 3,072 bytes
base_1: the heap segment's base, 0xA000
PA: the physical address
In words: address 0x1068 is 104 bytes into the heap, which is inside the 3 KiB segment, so it lands at 0xA000 + 0x068 = 0xA068.
```

Virtual 0x0C10 is segment 00 (code), offset 0xC10 (3,088). That exceeds the 2 KiB (2,048) code segment, so the access faults. This is where the term **segmentation fault** comes from; Linux uses SIGSEGV for invalid accesses; native x86-64 Linux primarily enforces process memory isolation through paging rather than segment bounds.

Segments also carry **protection bits**. Code can be marked read-and-execute only, which makes it safe to **share** one copy of a program's code between many processes.

But segments are still variable-sized and contiguous, so segmentation still suffers **external fragmentation**. The OS has to search for holes (best fit, first fit) or periodically **compact** memory by copying segments together, which is slow. A heap segment that needs to grow may also find no free space next to it.

## Key takeaways
- Segment bits select a base and a limit; the remaining bits select an offset.
- Read-only segments can share backing, but variable-sized contiguous segments still fragment.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
