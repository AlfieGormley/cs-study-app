---
id: isa-memory-contract
title: The ISA contract and shared memory paths
level: basic
minutes: 3
sourceLesson: isa-stored-program
summary: Distinguish architectural compatibility from implementation and compare memory organisations.
---

## What an ISA promises

The **instruction set architecture** (ISA) is the contract between software and hardware. It specifies:

- the instructions and how each is encoded in bits,
- the registers and their sizes,
- how memory is addressed (byte addressing, alignment rules, endianness),
- what happens on errors, interrupts and system calls,
- the privilege levels (user mode vs kernel mode).

The ISA deliberately does *not* say how the chip is built. That is the **microarchitecture**. AMD Zen and Intel Core designs both implement x86-64 but are very different inside. Apple's M-series and AWS Graviton chips both implement ARM64. Binary compatibility also requires the instructions and extensions actually used, a compatible OS and ABI, executable format, and required libraries. An ARM64 macOS binary does not therefore run unchanged on an ARM64 Linux server.

This separation is why your old programs still run on new hardware. A CPU must preserve the ISA’s observable behaviour. Many implementations overlap instructions (pipelining), issue several per cycle (superscalar), and execute out of order. This does not promise sequential consistency between threads: the ISA’s memory-ordering rules still apply. The next module covers how.

## Von Neumann, Harvard and the bottleneck

Because code and data share one memory and one path to the CPU, fetching instructions and loading data compete for the same memory bus. John Backus called this the **von Neumann bottleneck** in 1977. Main-memory latency and bandwidth can limit execution; caches and prefetching can reduce that pressure. A universal claim about the fraction of chip area occupied by caches is omitted because it requires measurements of a specified chip.

The alternative is the **Harvard architecture**: separate memories (and buses) for instructions and data. Many microcontrollers and DSPs work this way; on an AVR (the chip in classic Arduinos) the program sits in flash memory and data in SRAM.

A common modern general-purpose arrangement is called **modified Harvard** (the exact cache hierarchy is chip-specific):

| Level | Code and data |
|---|---|
| L1 cache | split: L1i and L1d |
| L2, L3 | unified |
| Main memory | one address space |

The split L1 lets the CPU fetch instructions and load data in the same cycle. Programmers still see one address space, while instructions and data can use separate cache paths.

## Key takeaways
- The ISA defines software-visible behaviour; microarchitecture implements it.
- Binary compatibility also needs the right extensions, ABI and operating system.
- Split instruction/data caches reduce contention without requiring separate programmer address spaces.

## Further reading
- [Von Neumann architecture — Wikipedia](https://en.wikipedia.org/wiki/Von_Neumann_architecture)
- [Instruction cycle — Wikipedia](https://en.wikipedia.org/wiki/Instruction_cycle)
- [Manchester Baby — Wikipedia](https://en.wikipedia.org/wiki/Manchester_Baby)
- [Modified Harvard architecture — Wikipedia](https://en.wikipedia.org/wiki/Modified_Harvard_architecture)
- [Little man computer — Wikipedia](https://en.wikipedia.org/wiki/Little_man_computer)
- [Self-modifying code — Wikipedia](https://en.wikipedia.org/wiki/Self-modifying_code)

### Primary references for this review
- [Manchester’s account of the Baby](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html)
- [Intel APX register extension](https://www.intel.com/content/www/us/en/developer/articles/technical/advanced-performance-extensions-apx.html)
- [Arm: implementing cache maintenance](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-implementing-clear-cache)
- [Arm: code updates across threads](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-working-with-threads)
- [Apple: porting JIT compilers](https://developer.apple.com/documentation/apple-silicon/porting-just-in-time-compilers-to-apple-silicon)
- [QEMU translation internals](https://www.qemu.org/docs/master/devel/tcg.html)
