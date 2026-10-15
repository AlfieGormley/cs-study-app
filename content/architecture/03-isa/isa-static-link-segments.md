---
id: isa-static-link-segments
title: Static archive resolution and executable segments
level: advanced
minutes: 3
sourceLesson: isa-compile-link-load
summary: Explain archive order and distinguish the linker’s view from the loader’s view.
---

## Static linking

A linker such as GNU `ld`, `gold`, LLVM `lld` or `mold` does two jobs.

**1. Symbol resolution.** Resolve symbol references according to binding and visibility rules. Undefined weak symbols and dynamic imports are exceptions to a simple one-definition model.

- No definition: `undefined reference to 'foo'`.
- Two strong definitions: `multiple definition of 'foo'`.
- With traditional GNU ld archive processing, static archives (`libfoo.a`) are searched **in command-line order**, and only members that satisfy a currently undefined symbol are pulled in. So `gcc -lm main.o` can fail where `gcc main.o -lm` works: when that archive was first considered, the required reference had not yet appeared. Archive groups can cause repeated searches; other linkers such as LLD have different backward-reference handling.

**2. Relocation.** Lay out all the sections in the output, assign each symbol a final address, then walk the relocation list and patch every hole.

A fully static executable contains copies of every library function it uses. This reduces dependencies on shared-library files for the linked code, but does not remove all runtime resources or guarantee faster startup or a larger final binary, and every program must be relinked to pick up a library security fix.

## Sections versus segments

An executable has two views of the same bytes. **Sections** are for the linker and tools. **Segments** (listed in the program headers) tell the loader what to map into memory, and with which permissions. `readelf -lW` on a typical PIE shows, simplified:

```
Type      Flags  Contents
PHDR      R      program headers
INTERP    R      /lib64/ld-linux-...
LOAD      R      headers, .dynsym...
LOAD      R E    .text .plt
LOAD      R      .rodata
LOAD      RW     .data .bss .got
DYNAMIC   RW     dynamic-link info
GNU_STACK RW     stack: not exec
GNU_RELRO varies  protect after relocation
```

This schematic has no RWX load segment; actual linker output and permission flags vary. GNU_STACK describes stack policy, and GNU_RELRO identifies a range to protect rather than adding another independent mapping. Note that no LOAD entry shown is both writable and executable. That is deliberate, and it matters for security below.

## Key takeaways
- Traditional GNU ld searches archives in command-line order.
- Static linkage does not eliminate every runtime resource dependency.
- Sections support linking; program headers describe runtime segments and other metadata.

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
