---
id: isa-elf-process-startup
title: From execve through the loader to main
level: advanced
minutes: 3
sourceLesson: isa-compile-link-load
summary: Trace conventional Linux/glibc startup and identify the initial stack metadata.
---

## Loading: from execve to main

An ELF executable’s entry point is machine code, not its C `main` function. For a conventional dynamically linked glibc ELF program on Linux, the kernel, interpreter and C runtime each perform part of the handoff:

1. The kernel's `execve` reads the ELF header and program headers, and maps each `LOAD` segment with its permissions.
2. Because there is an `INTERP` segment, it also maps the dynamic loader (`/lib64/ld-linux-x86-64.so.2`).
3. It builds the initial stack: `argc`, `argv`, `envp`, and an **auxiliary vector** (page size, entry point address, a pointer to 16 random bytes, and so on). Then it jumps to the *loader's* entry point.
4. `ld.so` maps dependencies, performs required relocations (leaving lazy slots where applicable), and runs loader-managed initialization before transferring to the program's `_start`.
5. `_start` calls `__libc_start_main`, which handles remaining initialization, including the main executable’s initialization functions in the glibc 2.39 path reviewed here, then invokes main. The third envp parameter is a platform extension, not the ISO C two-argument main signature.

You can watch this with `LD_DEBUG=libs ./prog` or `strace ./prog`, which shows the `mmap` calls for each library before your code runs.

## Key takeaways
- The kernel maps the ELF executable and its declared interpreter.
- The initial stack includes arguments, environment and auxiliary-vector metadata.
- Loader and libc startup cooperate before main; exact responsibilities are implementation-specific.

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
