---
id: isa-got-plt-binding
title: PIC, the GOT and lazy or eager binding
level: advanced
minutes: 3
sourceLesson: isa-compile-link-load
summary: Trace an external call and understand what full RELRO protects.
---

## Dynamic linking

Most programs link against **shared libraries** (`libc.so.6`) instead. The executable records only which libraries it needs (`DT_NEEDED` entries; inspect them with `readelf -d`). Processes mapping the same unchanged library file can share its pages of code. Replacing a library file normally benefits newly started processes; existing processes can retain the old mapping until restarted. ABI compatibility, Linux containers and bundled copies also matter.

The catch: the library's load address is selected at run time and can differ between processes. Code must still be able to find functions and globals in other modules without the loader rewriting the pages of code, which would stop them being shared.

### PIC and the GOT

Shared libraries commonly use **position-independent code** (PIC). Code refers to its own functions and data with `rip`-relative addressing (or `adrp` on ARM64), which works wherever the module is loaded.

For symbols requiring runtime address resolution, a common PIC mechanism uses a table of pointers in the module's writable data: the **Global Offset Table** (GOT). The loader resolves applicable GOT entries; some function slots can instead be bound lazily. The code reads the pointer from the GOT, again `rip`-relatively, and uses it:

```
mov  rax, [rip + environ@GOTPCREL]
mov  rax, [rax]     # value of environ
```

This mechanism relocates pointer slots rather than rewriting those instruction bytes; other writable data or relocation targets can still differ per process, while the code stays read-only and shared.

### The PLT and lazy binding

External calls can go through the **Procedure Linkage Table** (PLT), a set of small stubs in the executable's code. Classic x86-64 lazy binding works like this:

```
puts@plt:
    jmp   [rip + puts@GOT]
    push  0             # reloc index
    jmp   .plt0         # to resolver
```

1. `main` executes `call puts@plt`.
2. The stub jumps through puts's GOT slot. On the **first** call, that slot points back at the stub's own `push`.
3. The stub pushes the relocation index and jumps to `.plt0`, which calls the dynamic loader's resolver.
4. The resolver looks `puts` up in the loaded libraries, **writes its real address into the GOT slot**, and jumps to it.
5. Every **later** call goes stub → GOT → `puts` directly: one extra indirect jump.

Lazy binding can reduce startup resolution work for programs that link against thousands of functions but call few of them. The alternative, `-z now` (or `LD_BIND_NOW=1`), requests eager binding of the object’s required dynamic symbols at load time. Combined with **full RELRO** (`-z relro -z now`), the loader then makes the GOT read-only, so ordinary writes cannot overwrite the protected GOT slots. Other writable control data and permission-changing capabilities remain separate concerns. `-fno-plt` goes further and calls through the GOT directly, skipping the stub.

## Key takeaways
- PIC can keep instruction pages shareable while resolving external addresses in data.
- Classic lazy PLT binding updates a GOT slot on the first call.
- Eager resolution lets full RELRO protect applicable GOT slots after relocation.

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
