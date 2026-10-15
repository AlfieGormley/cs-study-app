---
id: mem-private-addresses
sourceLesson: mem-address-spaces
title: Virtual addresses and private memory
level: basic
minutes: 4
summary: A pointer names a location in a process address space, rather than directly identifying installed RAM.
---

Run two copies of the same program and print the address of a global variable in each. With a non-PIE executable, disabled address randomization, or a parent/child created by `fork`, the address can match while each process has its own value. Independent ASLR-enabled PIE executions generally choose different layouts. Both statements are true because the address the program sees is interpreted through a mapping rather than directly identifying a physical RAM location.

That illusion is **virtual memory**. Every process gets its own private **address space**: a huge, clean range of addresses that looks as if it belongs to that process alone. The operating system and the hardware quietly map those addresses onto real memory.

This unit introduces that mapping model. The following units explain isolation, early base-and-bounds and segmentation schemes, then paging.

## Physical and virtual addresses

A **physical address** identifies a location in the machine's physical address space, which can include RAM, device mappings and holes. 16 GiB contains 17,179,869,184 bytes, but installed RAM need not occupy one contiguous range of physical addresses.

A **virtual address** is what a program uses: every pointer in C, every instruction fetch, every stack push. With four-level x86-64 paging, the lower canonical half spans 128 TiB; five-level paging expands it to 64 PiB. The card below shows the corresponding powers of two. Actual usable mappings are constrained by kernel policy and reserved regions.

Those sizes all come from one rule: an address is a binary number, and every extra bit doubles how many different bytes it can name. Memory sizes are therefore powers of two, and the binary units (KiB, MiB, GiB and so on) are powers of two as well:

```formula
N = 2^n
16 GiB = 2^4 × 2^30 B = 2^34 B
2^47 B = 2^7 × 2^40 B = 128 TiB
2^56 B = 2^6 × 2^50 B = 64 PiB
where
N: the number of different bytes an address can name, which is the size of the address space in bytes
n: the number of bits in the address
2^n: n copies of 2 multiplied together; for example 2^10 = 1,024 and 2^4 = 16. Multiplying powers of two adds their exponents: 2^4 × 2^30 = 2^34
B: byte, 8 bits; each address names one byte
GiB: gibibyte, 2^30 bytes (1,073,741,824 B)
TiB: tebibyte, 2^40 bytes, or 1,024 GiB
PiB: pebibyte, 2^50 bytes, or 1,024 TiB
In words: n address bits can name 2^n bytes, so 34 bits cover 16 GiB, the 47 bits of the lower canonical half cover 128 TiB, and 56 bits cover 64 PiB.
```

For example, a 32-bit byte address can name 4 GiB, by the same rule: that is the address-space limit, before any user/kernel split or reserved mappings. The formula counts addresses, not memory: it says nothing about how much RAM is actually installed or mapped.

On every single memory access, a piece of hardware in the CPU called the **memory management unit (MMU)** translates the virtual address into a physical one, using tables the OS set up.

```
 process A          MMU           RAM
 0x4000 ----+                +---------+
            +--> translate ->| frame 7 |
 process B  |    (A's map)   |  ...    |
 0x4000 ----+--> translate ->| frame 2 |
                 (B's map)   +---------+
```

Same virtual address, different physical location, because each process has its own map.

## Key takeaways
- A pointer names a location in a process address space, rather than directly identifying installed RAM.
- Address-bit counts describe possible addresses; mappings and RAM capacity are separate limits.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
