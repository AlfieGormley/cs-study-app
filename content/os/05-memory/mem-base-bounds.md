---
id: mem-base-bounds
sourceLesson: mem-address-spaces
title: Translating with a base and a bound
level: basic
minutes: 4
summary: Check the virtual offset against the region size before adding its physical base.
---

## Base and bounds

The simplest hardware translation, used on machines in the 1960s, is **base and bounds** (also called dynamic relocation). The CPU has two registers per running process:

- the **base register**: where the process's memory starts in physical RAM;
- the **bounds register** (or limit register): how big it is.

On every access the hardware does two things: a check (is the address inside the process's region?) and an add (where does the region start in RAM?). As a formula:

```formula
PA = VA + base   for 0 ≤ VA < bounds
where
PA: the physical address: the byte's real location in RAM
VA: the virtual address the program used, counted from 0 at the start of the process's own space
base: the base register: the physical address where the process's region starts
bounds: the bounds register: the size of the region in bytes, so the legal virtual addresses run from 0 to bounds − 1
≤: less than or equal to
<: strictly less than
In words: every legal virtual address is moved up by the base; an address at or beyond the bounds is illegal, and the hardware raises a fault instead of translating it.
```

The same logic as hardware pseudocode:

The following Python fragment models nonnegative, width-limited addresses; the surrounding simulator supplies the registers and a fault exception.

```python
# Reject offsets outside the region.
if virtual >= bounds:
    raise fault        # protection
physical = virtual + base
```

A worked example: a process is loaded at physical 32 KiB (a base of 32,768) with a bounds of 16 KiB (16,384 bytes).

```formula
VA = 3,000 < 16,384 = bounds
PA = VA + base
PA = 3,000 + 32,768 = 35,768
where
VA: the virtual address the program used; here byte 3,000
bounds: the bounds register, the size of the region; here 16,384 bytes (16 KiB)
PA: the physical address the hardware actually accesses
base: the base register; here 32,768 (32 KiB)
In words: virtual 3,000 is inside the 16 KiB region, so the hardware adds the 32 KiB base and the access goes to physical byte 35,768.
```

Virtual 20,000 is at or above 16,384, so the hardware raises a fault instead; an unhandled illegal access normally terminates the process. The scheme assumes the process's whole region is one contiguous block of RAM, which is where its weaknesses come from.

On a context switch, the OS saves one process's base and bounds and loads the next. Only the kernel may change these registers; otherwise a process could simply point its base at someone else's memory.

Base and bounds gives relocation and protection cheaply, but it has two serious flaws:

- **Wasted space inside the process.** The whole address space must be contiguous in RAM, including the unused gap between heap and stack. A process with a large virtual range but little actual data still reserves the lot.
- **External fragmentation.** As processes of different sizes come and go, free RAM ends up as scattered holes. You may have 100 MiB free in total but no single hole big enough for a 20 MiB process.

## Key takeaways
- Check the virtual offset against the region size before adding its physical base.
- A single contiguous process region wastes gaps and suffers external fragmentation.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
