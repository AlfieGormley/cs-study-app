---
id: isa-aslr-guessing-leaks
title: ASLR, PIE, guessing models and address leaks
level: advanced
minutes: 3
sourceLesson: isa-compile-link-load
summary: Calculate hypothetical guessing work and explain why an address leak can defeat it.
---

NX restricts instruction fetches but permits reuse of existing executable code. Address randomisation adds a different obstacle: an attacker first needs to identify the relevant addresses.

### ASLR: unpredictable addresses

Code-reuse attacks need to know *where* things are. **Address space layout randomisation** places the stack, heap, `mmap` regions, shared libraries and (for PIE binaries) the executable itself at randomized addresses when enabled, subject to platform constraints; repeated addresses remain possible.

- Linux controls it with `/proc/sys/kernel/randomize_va_space` (2 adds heap randomization to mode 1; defaults depend on kernel configuration and system policy).
- The executable is randomised only if it is built as a **PIE** (typically ELF Type DYN, but DYN also describes shared objects). Compiler defaults are toolchain-specific; use `-fPIE -pie` explicitly when appropriate, which is one reason the jump tables in the previous lesson use relative offsets.
- Randomisation is measured in **bits of entropy**: b bits means 2 to the power b equally likely positions. If the position stays fixed while an attacker tries each candidate once, the average number of tries is:

```formula
N = 2^b
G = (N + 1) / 2
G = (2^8 + 1) / 2 = 257 / 2 = 128.5
where
N: the number of equally likely positions
b: the bits of entropy
G: the average number of guesses needed, counting the successful one
In words: each extra bit doubles the guessing work, and on average the attacker finds the position halfway through the list; 8 bits of entropy means about 128 tries.
```

- This assumes the address stays put between guesses; a target that re-randomises after every failure needs N tries on average instead. Address width permits more randomization space but does not determine effective entropy. A fixed default-bit count and universal attack-time estimate are omitted because architecture, kernel configuration and deployment determine them.

Limits: ASLR randomises a module's *base*, and everything inside keeps its relative position. With a matching binary and a correctly identified symbol, a leaked address can reveal that module’s base and the locations of objects at known offsets. Arbitrary leaked pointers, symbol interposition and indirect-function implementations need additional identification. A forked child inherits its parent's existing mapping addresses; subsequent mapping changes or exec can make their layouts diverge. KASLR can also randomize the kernel base when supported and enabled.

## Key takeaways
- ASLR and PIE randomise eligible mappings under platform policy.
- Uniform guessing models must state whether the target changes between attempts.
- An identified symbol leak may reveal other known offsets within the matching module.

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
