---
id: isa-build-objects-relocations
title: From source to object files and relocation records
level: advanced
minutes: 4
sourceLesson: isa-compile-link-load
summary: Follow the build stages and calculate a concrete PLT32 relocation.
---

Typing `gcc hello.c` feels like one step. It has preprocessing, compilation, assembly and linking stages (which need not be separate programs or materialized files), and then the kernel and a dynamic loader cooperate to turn the final file into a process.

Knowing these steps explains error messages you will meet ("undefined reference", "relocation truncated", "cannot find -lfoo"), why lazy binding can add work to a first library call, and where the operating system's memory-safety defences come from.

## The build steps

```flow
hello.c: C source
cpp: preprocess #include and #define
hello.i: preprocessed source
cc1: compile to assembly
hello.s: assembly
as: assemble to machine code
hello.o: relocatable object
ld: link with libc and crt files
a.out: executable
execve + ld.so: load and run
Running process
```

`gcc -save-temps hello.c` keeps every intermediate file so you can look at each. `gcc -v` prints the exact commands the driver runs, including the start-up objects (`crt1.o`, `crti.o` and friends) it links in for you.

The interesting boundary is between the assembler and the linker. In ordinary separate compilation a compiler processes one translation unit at a time (link-time optimization can cross that boundary), so when `hello.c` calls `puts`, nobody yet knows where `puts` will live.

## Object files: code with holes

The assembler produces a **relocatable object file**. On Linux it is in **ELF** (Executable and Linkable Format), the same format used for executables, shared libraries and core dumps. An object file contains:

- **Sections**: `.text` (code), `.rodata` (constants and string literals), `.data` (initialised globals), `.bss` (zero-initialised globals, whose zero-filled payload occupies no file bytes; section metadata still exists).
- A **symbol table**: names this file defines (`main`) and names it uses but doesn't define (`puts`, marked undefined).
- **Relocations**: a list of locations in code or data that may require fixups once final addresses are known.

Disassembling `hello.o` with `objdump -dr` shows the hole:

```
e8 00 00 00 00   call  <main+0x9>
     R_X86_64_PLT32  puts-0x4
```

The `call` is encoded with a zero displacement, and the relocation entry says: "when you know where `puts` (or its PLT stub) is, put the PC-relative distance here, minus 4 because the displacement is measured from the end of the instruction". The linker's calculation is:

```formula
disp = L + A − P
disp = L − (P + 4)
disp = 0x401030 − 0x401009 = 0x27
where
disp: the signed 32-bit value the linker writes into the call's 4-byte displacement field
L: the address of puts's PLT stub, puts@plt (here 0x401030); if the linker can resolve the call directly, it uses puts itself
A: the addend stored in the relocation entry: −4 here
P: the address of the displacement field itself, 1 byte after the e8 opcode (here 0x401005 for a call at 0x401004)
4: the field is 4 bytes long, so P + 4 is the end of the instruction, the point the CPU measures from
In words: the hole gets the distance from the end of the call instruction to the target; with the call ending at 0x401009 and puts@plt at 0x401030, that is 0x27 (39) bytes forwards.
```

The addresses here are illustrative (`main` at 0x401000, so the `call` at `main+0x4` ends at `main+0x9`); the x86-64 psABI defines `R_X86_64_PLT32` as L + A − P.

## Key takeaways
- The compiler driver coordinates preprocessing, compilation, assembly and linking.
- ELF objects carry sections, symbols and relocations.
- A call relocation tells the linker how to fill the displacement field.

## Further reading
- [Executable and Linkable Format — Wikipedia](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format)
- [elf(5) — Linux manual page](https://man7.org/linux/man-pages/man5/elf.5.html)
- [ld.so(8) — Linux manual page](https://man7.org/linux/man-pages/man8/ld.so.8.html)
- [Position Independent Code in shared libraries — Eli Bendersky](https://eli.thegreenplace.net/2011/11/03/position-independent-code-pic-in-shared-libraries/)
- [All about Procedure Linkage Table — MaskRay](https://maskray.me/blog/2021-09-19-all-about-procedure-linkage-table)
- [How To Write Shared Libraries — Ulrich Drepper (PDF)](https://www.akkadia.org/drepper/dsohowto.pdf)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [NX bit — Wikipedia](https://en.wikipedia.org/wiki/NX_bit)
- [Buffer overflow protection — Wikipedia](https://en.wikipedia.org/wiki/Buffer_overflow_protection)
- [GCC instrumentation options (-fstack-protector)](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)

### Primary implementation references
- [GNU ld options and archive/RELRO rules](https://sourceware.org/binutils/docs/ld/Options.html)
- [Linux ASLR control](https://docs.kernel.org/admin-guide/sysctl/kernel.html#randomize-va-space)
- [glibc 2.39 stack-guard setup](https://github.com/bminor/glibc/blob/glibc-2.39/sysdeps/unix/sysv/linux/dl-osinfo.h)
- [glibc 2.39 startup](https://github.com/bminor/glibc/blob/glibc-2.39/csu/libc-start.c)
