---
id: proc-process-memory-layout
sourceLesson: proc-process-abstraction
title: "Reading a virtual address-space layout"
level: basic
minutes: 4
summary: "Virtual addresses identify mappings in a particular address space, not unique physical locations."
---

Virtual addresses identify mappings in a particular address space, not unique physical locations. This lesson focuses on reading a virtual address-space layout.

## The address space

Each process sees a **virtual address space**: a range of addresses that the MMU translates to physical RAM using per-process page tables. Two processes can both use address `0x400000` and see completely different data.

The following is a schematic of a conventional Linux x86-64 layout (low addresses at the bottom), not an exact map. With four-level paging the low user range spans 128 TiB; a large non-canonical gap separates it from high kernel addresses. Five-level paging supports a larger range.

Where does 128 TiB come from? Four-level paging translates 48-bit virtual addresses, and Linux gives the lower half of that range to user space and the upper half to the kernel:

```formula
S_user = 2^{n − 1} B
S_user = 2^{48 − 1} B = 2^47 B
S_user = 140,737,488,355,328 B
S_user = 128 TiB
where
S_user: the size of the user part of each process's virtual address space, in bytes (B)
n: the number of virtual-address bits the page tables translate: 48 with four-level paging, 57 with five-level paging
B: byte, 8 bits
TiB: tebibyte, 2 to the power 40 bytes (1,099,511,627,776 B), so 2^47 B is 2^7 = 128 TiB
In words: 48 address bits can name 2^48 bytes; half of those, 128 TiB, belong to user space.
```

A process only uses a tiny part of that range; the rest is simply unmapped. With five-level paging (57 bits) the same halving gives 64 PiB of user space, though Linux only hands out addresses above 128 TiB to programs that ask for them.

```
 0xffff...  +--------------------+
            | kernel (no access) |
 ~128 TiB   +--------------------+
            | stack  (grows down)|
            |        v           |
            |                    |
            | mmap region:       |
            | shared libs, big   |
            | mallocs, mapped    |
            | files              |
            |        ^           |
            | heap   (grows up)  |
            +--------------------+
            | BSS  (zeroed data) |
            | data (init'd data) |
            | rodata (constants) |
            | text (code)        |
 0x0        +--------------------+
            (page 0 unmapped)
```

| Region | Holds | Permissions |
|---|---|---|
| text | machine code | read + execute |
| rodata | string literals, `const` globals | read |
| data | initialised globals and statics | read + write |
| BSS | zero or uninitialised globals | read + write |
| heap | `malloc` memory | read + write |
| mmap | shared libs, large allocations | varies |
| stack | locals, return addresses | read + write |

Some details that matter:

- **Text is read-only and shared.** Processes using the same executable can share file-backed code pages. An ordinary write to a read-only mapping faults; mappings and permissions can differ.
- **BSS costs nothing on disk.** The executable records only its size; the kernel maps zero-filled pages at load time. A 100 MB `static char buf[100000000];` doesn't make your binary 100 MB.
- **The heap** grows with the `brk` syscall. glibc may use separate `mmap` allocations for requests not served by its free lists above a threshold initially 128 KiB and normally adjusted dynamically. Arenas and tunables also affect placement.
- **The stack** grows downwards as functions are called. Its limit is environment-dependent; an illustrative 8 MiB limit appears as 8192 KiB in `ulimit -s`. Deep recursion past the limit hits an unmapped guard region and the process gets `SIGSEGV`.
- **Page zero is normally unmapped** on ordinary Linux deployments. Null dereference is undefined in C, so the language itself does not guarantee a particular signal.
- **ASLR** (address space layout randomisation) can randomise the stack, heap, libraries and (for position-independent executables) the text at program launch, making exploits harder.
- **Kernel mappings** are inaccessible to ordinary user-mode code. With KPTI, the user page tables contain only minimal kernel-entry mappings; the full kernel map is selected on entry.



## Key takeaways
- Virtual addresses identify mappings in a particular address space, not unique physical locations.
- Text, BSS, heap, mapped regions and stack have distinct roles; actual placement depends on the implementation.

## Further reading
- [The Abstraction: The Process — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [The Abstraction: Address Spaces — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [proc(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Process control block — Wikipedia](https://en.wikipedia.org/wiki/Process_control_block)
- [Process state — Wikipedia](https://en.wikipedia.org/wiki/Process_state)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Linux x86-64 memory map](https://docs.kernel.org/arch/x86/x86_64/mm.html)
- [glibc allocator tuning](https://man7.org/linux/man-pages/man3/mallopt.3.html)
