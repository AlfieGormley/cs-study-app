---
id: mem-address-spaces
title: Address spaces and why virtual memory exists
level: basic
minutes: 12
summary: Physical versus virtual addresses, what an address space gives each process, and the historical base-and-bounds and segmentation schemes that paging replaced.
---

Run two copies of the same program and print the address of a global variable in each. With a non-PIE executable, disabled address randomization, or a parent/child created by `fork`, the address can match while each process has its own value. Independent ASLR-enabled PIE executions generally choose different layouts. Both statements are true because the address the program sees is not where the data actually lives in RAM.

That illusion is **virtual memory**. Every process gets its own private **address space**: a huge, clean range of addresses that looks as if it belongs to that process alone. The operating system and the hardware quietly map those addresses onto real memory.

This lesson explains why that illusion is worth the effort, and walks through the early hardware schemes (base and bounds, then segmentation) that led to paging, which the rest of the module covers.

## Physical and virtual addresses

A **physical address** identifies a location in the machine's physical address space, which can include RAM, device mappings and holes. 16 GiB contains 2^34 bytes, but installed RAM need not occupy the contiguous range 0 through 2^34−1.

A **virtual address** is what a program uses: every pointer in C, every instruction fetch, every stack push. With four-level x86-64 paging, the lower canonical half spans 2^47 bytes (128 TiB); five-level paging expands it to 2^56 bytes (64 PiB). Actual usable mappings are constrained by kernel policy and reserved regions.

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

## Before virtual memory

The earliest machines ran one program at a time, loaded at a fixed physical address. The program used physical addresses directly. That works until you want to run several programs at once (**multiprogramming**), and then three problems appear:

1. **Relocation.** Code containing fixed absolute addresses needs relocation or a translation mechanism when loaded elsewhere; position-independent code and relative addressing can reduce relocation work.
2. **Protection.** Nothing stops a buggy program writing over another program, or over the OS itself.
3. **Capacity.** Every program must fit in physical memory at once, and its size is limited by whatever contiguous space is free.

Virtual memory solves all three. In the framing of the OSTEP textbook, a good virtual memory system offers:

- **Transparency**: programs behave as if they have private memory and need no special code.
- **Efficiency**: translation must be fast (hardware does it) and the tables must not waste much space.
- **Protection and isolation**: a process cannot read or write memory outside its own address space, and it cannot touch the kernel's memory from user mode.

It also enables things the early designers did not have: sharing read-only library pages between processes, lazily allocating memory only when it is touched, and running programs whose memory is larger than RAM by spilling some to disk.

## Seeing it in C

This program forks a child. The child changes a global; the parent then prints the same variable.

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int x = 1;

int main(void) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }
    if (pid == 0) {             /* child */
        x = 2;
        printf("child  %p %d\n",
               (void *)&x, x);
        return 0;
    }
    wait(NULL);                 /* parent */
    printf("parent %p %d\n", (void *)&x, x);
    return 0;
}
```

Illustrative output (the address varies):

```
child  0x55e4c3a1b010 2
parent 0x55e4c3a1b010 1
```

The child is a copy of the parent, so `x` sits at the same *virtual* address in both. But they have separate address spaces, so the child's write lands in a different physical frame and the parent still sees 1. (Lesson 4 explains how Linux makes this copy cheaply with copy-on-write.)

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
- On x86-64, addresses are **canonical**: with 4-level paging, bits 63 to 47 must all be equal. Linux gives the lower half (0 to `0x00007fffffffffff`) to user space and keeps the upper half for the kernel.
- **Traditionally, kernel mappings appear in each process's page tables**, but its pages are marked supervisor-only, so user code gets a fault if it touches them. (After the 2018 Meltdown attack showed CPUs could leak that data speculatively, Linux added *kernel page-table isolation*, which unmaps most of the kernel while user code runs.)

## Base and bounds

The simplest hardware translation, used on machines in the 1960s, is **base and bounds** (also called dynamic relocation). The CPU has two registers per running process:

- **base**: where the process's memory starts in physical RAM;
- **bounds** (or limit): how big it is.

On every access the hardware does:

```
if virtual >= bounds:
    raise fault        # protection
physical = virtual + base
```

> [!example] Base and bounds
> A process is loaded at physical 32 KiB (base = 32,768) with bounds = 16 KiB (16,384).
> - Virtual 3,000 is below 16,384, so physical = 3,000 + 32,768 = **35,768**.
> - Virtual 20,000 is at or above 16,384, so the hardware raises a fault; an unhandled illegal access normally terminates the process.

On a context switch, the OS saves one process's base and bounds and loads the next. Only the kernel may change these registers; otherwise a process could simply point its base at someone else's memory.

Base and bounds gives relocation and protection cheaply, but it has two serious flaws:

- **Wasted space inside the process.** The whole address space must be contiguous in RAM, including the unused gap between heap and stack. A process with a large virtual range but little actual data still reserves the lot.
- **External fragmentation.** As processes of different sizes come and go, free RAM ends up as scattered holes. You may have 100 MiB free in total but no single hole big enough for a 20 MiB process.

## Segmentation

**Segmentation** generalises base and bounds: instead of one pair per process, there is one pair per logical **segment** (code, heap, stack and so on). Each segment can be placed anywhere in RAM independently, and the gap between heap and stack costs nothing.

The hardware needs to know which segment an address belongs to. One classic approach uses the top bits of the virtual address as a segment number.

> [!example] Segment translation
> A toy machine has 14-bit virtual addresses. The top 2 bits pick the segment and the low 12 bits are the offset.
>
> | Seg | Name | Base | Size |
> |---|---|---|---|
> | 00 | code | 0x8000 | 2 KiB |
> | 01 | heap | 0xA000 | 3 KiB |
>
> Virtual 0x1068 is `01 0000 0110 1000` in binary. Segment 01 (heap), offset 0x068 (104). 104 is less than 3 KiB, so physical = 0xA000 + 0x068 = **0xA068**.
>
> Virtual 0x0C10 is segment 00 (code), offset 0xC10 (3,088). That exceeds the 2 KiB (2,048) code segment, so the access faults. This is where the term **segmentation fault** comes from; Linux uses SIGSEGV for invalid accesses; native x86-64 Linux primarily enforces process memory isolation through paging rather than segment bounds.

Segments also carry **protection bits**. Code can be marked read-and-execute only, which makes it safe to **share** one copy of a program's code between many processes.

But segments are still variable-sized and contiguous, so segmentation still suffers **external fragmentation**. The OS has to search for holes (best fit, first fit) or periodically **compact** memory by copying segments together, which is slow. A heap segment that needs to grow may also find no free space next to it.

### The x86 story

Intel's processors carry the history with them:

- The **8086** (1978) formed a 20-bit physical address as `segment * 16 + offset`, mainly to reach 1 MiB with 16-bit registers.
- The **80286** added protected mode with segment descriptors holding base, limit and privilege level.
- The **80386** added **paging** underneath segmentation, and later 32-bit Linux systems used largely flat ordinary code/data segments with paging for isolation. Special segments and early Linux designs were exceptions.
- In **native x86-64 64-bit mode** (not its 32-bit compatibility submode), the hardware ignores the base and limit of the CS, DS, ES and SS segments. Only FS and GS bases survive, and they are used for thread-local storage (glibc points FS at each thread's TLS block).

For ordinary fixed-size page mappings, any suitable free frame can back a page. Physical fragmentation still matters for larger contiguous allocations, huge pages and device constraints. That is the subject of the next lesson.

## Where caches fit

CPU cache organization varies. A common design uses physical tags and a virtually indexed L1, allowing translation and cache-index lookup to overlap, but caches are a separate topic covered in the Computer Architecture subject. Here we care about the mapping, not about how fast RAM itself is.

## Pitfalls and misconceptions

- **"A pointer is a RAM address."** Not in user space. A pointer is meaningful only inside its own address space; passing its numeric value does not establish access in another process. Shared layouts can make pointers meaningful across processes; offsets within shared mappings are often more robust.
- **"Virtual memory means swap."** Swap is one feature built on virtual memory. Virtual memory is the translation layer, and it is in use on every access even on a phone with no swap at all.
- **"A big address space costs RAM."** The address space is mostly empty. Mappings can consume metadata and commit-accounting budget before resident pages are touched; resident backing, page tables and shared-page accounting also matter.

## Key takeaways
- Programs use virtual addresses; the MMU translates each one to a physical address using per-process tables set up by the OS.
- Virtual memory solves relocation, protection and capacity, and enables sharing and lazy allocation.
- Each Linux process has a mostly empty address space with code, data, heap, mmap and stack regions, randomised by ASLR; the kernel half is supervisor-only.
- Base and bounds adds a base and checks a limit: cheap, but wastes the gap inside the process and fragments RAM.
- Segmentation gives each logical region its own base and bounds; it still fragments externally, and x86-64 has all but abandoned it in favour of paging.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
