---
id: sys-elf-hardening
title: RELRO and fortified library calls
level: intermediate
minutes: 3
sourceLesson: sys-mitigations
summary: Full RELRO combines relocation-region protection with eager binding in a supported ELF layout.
---

## RELRO and FORTIFY_SOURCE

Two more toolchain hardening features are common on Linux:

- **RELRO** makes a designated ELF relocation region read-only after relocation. In a conventional supported ELF toolchain, full RELRO (`-Wl,-z,relro,-z,now`) also resolves lazy function bindings at load time so the GOT can be protected. Later `dlopen` loads have their own relocations. This does not protect every function pointer in a program.
- **`_FORTIFY_SOURCE`** adds compile-time diagnostics and run-time checks to supported library calls where object-size information is available. Level 3 uses dynamic object-size information and requires a compatible compiler/libc; glibc enables these wrappers only with optimisation. Unknown sizes and unsupported operations can remain unchecked.

An illustrative GNU/Linux ELF build fragment follows. It requires toolchain support for level-3 fortification; the CET-related flag is for supported x86 targets. Check platform documentation and the resulting binary/runtime configuration. Accepting a compiler flag does not prove that hardware enforcement is active.

```
# Compile with supported hardening.
CFLAGS += -O2 -fstack-protector-strong \
  -D_FORTIFY_SOURCE=3 -fPIE \
  -fcf-protection=full
# Resolve before protecting relocations.
LDFLAGS += -pie -Wl,-z,relro,-z,now
```

## Key takeaways
- Full RELRO combines relocation-region protection with eager binding in a supported ELF layout.
- Fortification covers supported calls when object-size information and toolchain requirements are satisfied.
- Check the generated binary and runtime configuration; accepted flags alone do not prove enforcement.

## Further reading
- [Source fortification — glibc](https://sourceware.org/glibc/manual/latest/html_node/Source-Fortification.html)
- [Compiler hardening guide — OpenSSF](https://best.openssf.org/Compiler-Hardening-Guides/Compiler-Options-Hardening-Guide-for-C-and-C++.html)
- [GNU linker options](https://sourceware.org/binutils/docs/ld/Options.html)
