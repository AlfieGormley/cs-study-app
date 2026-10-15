---
id: mem-linux-layout
sourceLesson: mem-address-spaces
title: Reading a Linux address-space layout
level: basic
minutes: 3
summary: Canonical-address rules and mapping permissions constrain usable pointers.
---

## What an address space looks like

A typical Linux x86-64 process maps selected regions of a much larger address range. This schematic assumes four-level paging; real layouts and mappings vary:

```
 0x7fff_ffff_ffff  lower canonical limit
 +-----------------+
 | stack           |  grows down
 |      ...        |
 | mmap region     |  libraries, mmap()
 |      ...        |
 | heap            |  grows up (brk)
 | .bss / .data    |  globals
 | .text           |  code, read-only
 +-----------------+
 0x0000_0000_0000  (normally unmapped)
```

You can see the real map of any process in `/proc/<pid>/maps`. Each line shows a range, its permissions (`r-xp` for code, `rw-p` for data) and what backs it (a file or nothing).

Points worth knowing:

- **Page 0 is normally left unmapped** to catch null-address accesses. Minimum-mapping policy and privileges can allow exceptions; a C null-pointer dereference is undefined behavior, not a portable promise of SIGSEGV.
- **ASLR** randomizes selected mappings when enabled; relocating executable code requires a suitable PIE executable. It makes address prediction harder, not impossible. `fork` preserves the parent's layout, including any randomized addresses.
- For ordinary x86-64 addresses with address-tag masking disabled, the address must be a **canonical address**: with 4-level paging, bits 63 to 47 must all be equal. Linux gives the lower half (0 to `0x00007fffffffffff`) to user space and keeps the upper half for the kernel.
- **Traditionally, kernel mappings appear in each process's page tables**, but its pages are marked supervisor-only, so user code gets a fault if it touches them. (After the 2018 Meltdown attack showed CPUs could leak that data speculatively, Linux added *kernel page-table isolation*, which unmaps most of the kernel while user code runs.)

## Pitfalls and misconceptions

- **"A pointer is a RAM address."** Not in user space. A pointer is meaningful only inside its own address space; passing its numeric value does not establish access in another process. Shared layouts can make pointers meaningful across processes; offsets within shared mappings are often more robust.
- **"Virtual memory means swap."** Swap is one feature built on virtual memory. Virtual memory is the translation layer, and it is in use on every access even on a phone with no swap at all.
- **"A big address space costs RAM."** The address space is mostly empty. Mappings can consume metadata and overcommit-accounting budget before resident pages are touched; resident backing, page tables and shared-page accounting also matter.

## Key takeaways
- Canonical-address rules and mapping permissions constrain usable pointers.
- ASLR changes selected layouts; KPTI separates reduced user and full kernel views.
- Passing a pointer value does not arrange access to another process’s memory.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
