---
id: sys-elf-hardening
title: RELRO and fortified library calls
level: intermediate
minutes: 4
sourceLesson: sys-mitigations
summary: Full RELRO combines relocation-region protection with eager binding in a supported ELF layout.
---

## RELRO and FORTIFY_SOURCE

Two more toolchain hardening features are common on Linux:

- **RELRO** makes a designated ELF relocation region read-only after relocation. In a conventional supported ELF toolchain, full RELRO (`-Wl,-z,relro,-z,now`) also resolves lazy function bindings at load time so the GOT can be protected. Later `dlopen` loads have their own relocations. This does not protect every function pointer in a program.
- **`_FORTIFY_SOURCE`** adds compile-time diagnostics and run-time checks to supported library calls where object-size information is available. When a check fails at run time, glibc aborts the program with `SIGABRT`. Level 3 uses dynamic object-size information; glibc's headers treat it as level 2 unless the compiler is GCC 12 or later or Clang 9 or later. glibc enables these wrappers only when optimisation is on, so an `-O0` build gets no fortification. Upstream glibc's headers print a warning that `_FORTIFY_SOURCE` requires optimisation; Debian and Ubuntu remove that warning from their glibc packages, so there the checks are silently absent. Unknown sizes and unsupported operations can remain unchecked.

> [!analogy] Real-world analogy: laminating a phone list
> An office keeps a pencilled list of phone numbers and fills each one in the first time someone needs it, so the list must stay writable all day. Anyone passing could rub out a number and pencil in their own. A careful office looks up every number in the morning and then laminates the list.
>
> **How it maps:** The list is the GOT, which holds the addresses of library functions. Filling numbers in on first use is lazy binding. Looking everything up at start-up is eager binding (`-z now`), and laminating is RELRO making that region read-only, so a memory-corruption bug cannot redirect a library call by rewriting it.
>
> **Where it stops:** Only that list is laminated: other function pointers in the program stay writable, and a library loaded later with `dlopen` has its own list. Looking everything up in advance also costs some start-up time.

An illustrative GNU/Linux ELF build fragment follows. It requires toolchain support for level-3 fortification; the CET-related flag is for supported x86 targets. Check platform documentation and the resulting binary/runtime configuration. Accepting a compiler flag does not prove that hardware enforcement is active.

```
# Compile with supported hardening.
CFLAGS += -O2 -fstack-protector-strong \
  -D_FORTIFY_SOURCE=3 -fPIE \
  -fcf-protection=full
# Resolve before protecting relocations.
LDFLAGS += -pie -Wl,-z,relro,-z,now
```

To check a built binary, `readelf -d` should show `BIND_NOW` in its dynamic flags and `readelf -l` a `GNU_RELRO` segment for full RELRO. In a GCC 13 test on x86-64 Linux, the fragment's flags produced both. GCC on 64-bit Arm rejects `-fcf-protection=full`; without that flag, a GCC 14 Arm build also produced both. A build with `-z lazy -z norelro` produced neither.

## Key takeaways
- Full RELRO combines relocation-region protection with eager binding in a supported ELF layout.
- Fortification covers supported calls when object-size information and toolchain requirements are satisfied.
- Check the generated binary and runtime configuration; accepted flags alone do not prove enforcement.

## Further reading
- [Source fortification — glibc](https://sourceware.org/glibc/manual/latest/html_node/Source-Fortification.html)
- [Compiler hardening guide — OpenSSF](https://best.openssf.org/Compiler-Hardening-Guides/Compiler-Options-Hardening-Guide-for-C-and-C++.html)
- [GNU linker options](https://sourceware.org/binutils/docs/ld/Options.html)
