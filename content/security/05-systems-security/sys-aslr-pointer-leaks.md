---
id: sys-aslr-pointer-leaks
title: A pointer leak reveals one known layout
level: intermediate
minutes: 3
sourceLesson: sys-mitigations
summary: Subtract a known pointer offset to recover the base of that known library mapping.
---

ASLR can make a useful address hard to predict while an information leak makes it calculable. The important question is which build and which mapping the disclosed pointer identifies.

Two caveats make ASLR weaker than the numbers suggest:

1. **Leaks can weaken ASLR.** A pointer into a known library build at a known offset reveals that mapping base. It does not automatically reveal unrelated mappings or unknown builds.

For the ordinary fixed-layout library mapping in this example, the relevant symbols have known offsets from the mapping base. A leak that identifies that build and target can therefore reveal the base. Some objects are allocated separately or functions are resolved dynamically, so a symbol name alone does not prove that its actual run-time address has that simple relationship. With illustrative hexadecimal numbers:

```formula
A_base = P − o_P
A_base = 0x7f12345a1b20 − 0x2db20
A_base = 0x7f1234574000
A_T = A_base + o_T
A_T = 0x7f1234574000 + 0x50d70
A_T = 0x7f12345c4d70
where
A_base: the base address, where the library's mapping starts in this process
P: the leaked pointer value, an address inside that library
o_P: the known offset of the leaked pointer's target from the library start, read from the same build
A_T: the address of another target the attacker wants, such as a useful function
o_T: that target's known offset from the library start
0x7f12345a1b20: a hexadecimal (base-16) number, marked by the 0x prefix; the values here are made up for illustration
In words: subtract the leaked item's known offset to find where the library starts, then add another known offset to locate that target in the same mapping.
```

In this fixed-layout model, ASLR moves the base rather than the relative offsets, which is why that particular leak identifies the mapping. The illustrative base ends in three hexadecimal zeros, consistent with a 4 KiB page boundary: 4,096 bytes. Actual page sizes and mapping alignments depend on the platform.

2. **Not every mapping is randomised.** Conventional non-PIE ELF executables have fixed main-code addresses. PIE permits random placement when the loader and OS enable it; compiler flags alone are not proof of effective randomisation.

Linux can randomise its kernel base when **KASLR** is supported and enabled. A known-offset kernel pointer leak can weaken that protection.

## Key takeaways
- Subtract a known pointer offset to recover the base of that known library mapping.
- Knowing one mapping does not reveal every other mapping or disable NX and canaries.
- PIE enables random placement of main code when the loader and OS actually apply it.

## Further reading
- [Linux virtual-memory sysctls](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [ELF program format — Linux manual](https://man7.org/linux/man-pages/man5/elf.5.html)
- [Instrumentation options — GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
