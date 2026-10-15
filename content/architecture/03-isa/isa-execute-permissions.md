---
id: isa-execute-permissions
title: NX, W^X and the limits of execute permissions
level: advanced
minutes: 3
sourceLesson: isa-compile-link-load
summary: Explain what execute-disable prevents and why it does not remove memory vulnerabilities.
---

## Hardening: why the defences exist

An out-of-bounds access violates C/C++ rules and has undefined behaviour, but ordinary native code often lacks runtime bounds checks. In a vulnerable stack layout, a buffer can lie at lower addresses than saved registers and the **return address** (see the calling-convention units); actual layout depends on the compiler and function. An out-of-bounds write that is long enough can overwrite that address, so when the function returns, control goes somewhere an attacker chose.

Fixing every such bug is the real cure, and memory-safe languages remove whole classes of them. In the meantime, three widely used mitigations make these bugs much harder to turn into control of the machine. Each is a layer, and each has known limits.

### NX: data is not code

Early exploits placed machine code in the overflowing buffer and returned into it. **NX** (no-execute; Intel calls it XD, Windows calls the policy DEP, ARM has XN, UXN and PXN) uses architectural execute permissions. In x86-64 paging with NX supported and EFER.NXE enabled, bit 63 of relevant paging-structure entries can prohibit execution. If effective permissions prohibit execution, an instruction fetch faults.

A **W^X** policy aims to avoid simultaneously writable and executable mappings; enforcement and exceptions depend on the OS and configuration. The stack, heap and `.data` are non-executable in typical hardened layouts (`GNU_STACK RW` specifically requests a non-executable stack, not heap/data policy); `.text` is read-only.

Limits: NX blocks instruction fetches from non-executable mappings; it does not prevent injected code running in an executable mapping, or attacks that reuse existing code, chaining together fragments already in `.text` and libc (return-oriented programming). It also complicates JIT compilers, which must write code and then execute it; follow platform JIT permission, cache-maintenance and synchronization rules. Separate RW/RX aliases satisfy only a mapping-level W^X rule, not a stronger prohibition on writable access to executable backing memory.

## Key takeaways
- An out-of-bounds write can corrupt control data, so fixing the memory bug remains essential.
- NX checks instruction-fetch permission; it does not classify who created the bytes.
- W^X depends on its mapping or backing-memory policy; code reuse is a different problem.

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
