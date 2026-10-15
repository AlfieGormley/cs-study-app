---
id: mem-x86-segmentation
sourceLesson: mem-address-spaces
title: How x86 moved from segments to paging
level: basic
minutes: 3
summary: Real-mode segment arithmetic differs from protected-mode segment descriptors.
---

### The x86 story

Intel's processors carry the history with them:

- The **8086** (1978) formed a 20-bit physical address from a 16-bit segment value and a 16-bit offset, mainly to reach 1 MiB with 16-bit registers:

```formula
PA = (16seg + off) mod 2^20
2^20 B = 1,048,576 B = 1 MiB
where
PA: the 20-bit physical address
seg: the 16-bit value in a segment register
off: the 16-bit offset within the segment
mod: the remainder after division; retaining only the low twenty bits here
2^20: 20 copies of 2 multiplied together, the number of addresses 20 bits can name
B: byte
MiB: mebibyte, 2^20 bytes
In words: shift the segment value left four bits, add the offset, and keep the low twenty bits. On the original 8086 a carry beyond 1 MiB wraps to the start.
```

For example, segment 0x1234 and offset 0x0010 select physical byte 0x12350. The original 8086 retains only the low twenty address bits, so a sum beyond 1 MiB wraps; later real-mode hardware can enable an additional address bit, so wrapping rules differ. Many segment/offset pairs name the same byte.

- The **80286** added protected mode with segment descriptors holding base, limit and privilege level.
- The **80386** added **paging** underneath segmentation, and later 32-bit Linux systems used largely flat ordinary code/data segments with paging for isolation. Special segments and early Linux designs were exceptions.
- In **native x86-64 64-bit mode** (not its 32-bit compatibility submode), the hardware ignores the base and limit of the CS, DS, ES and SS segments. Only FS and GS bases survive, and they are used for thread-local storage (glibc points FS at each thread's thread-local storage block).

For ordinary fixed-size page mappings, any suitable free frame can back a page. Physical fragmentation still matters for larger contiguous allocations, huge pages and device constraints. That is the subject of the next lesson.

## Where caches fit

CPU cache organization varies. A common design uses physical tags and a virtually indexed L1, allowing translation and cache-index lookup to overlap, but caches are a separate topic covered in the Computer Architecture subject. Here we care about the mapping, not about how fast RAM itself is.

## Key takeaways
- Real-mode segment arithmetic differs from protected-mode segment descriptors.
- Native 64-bit x86 largely ignores ordinary segment bases and limits, while FS and GS bases remain useful.
- Translation and CPU caches solve different problems.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
