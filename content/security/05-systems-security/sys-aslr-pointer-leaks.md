---
id: sys-aslr-pointer-leaks
title: A pointer leak reveals one known layout
level: intermediate
minutes: 3
sourceLesson: sys-mitigations
summary: Subtract a known pointer offset to recover the base of that known library mapping.
---

ASLR can make a useful address hard to predict while an information leak makes it calculable. The important question is which build and which mapping the disclosed pointer identifies.

Two caveats make ASLR weaker than its entropy suggests.

## Leaks turn guessing into arithmetic

ASLR moves a library's whole mapping as one block. Inside it, every function and variable stays at the same **offset** from the start, because the offsets are fixed when that build of the library is linked. So a single leaked pointer at a known offset in a known build reveals where the whole mapping starts, and from there, where everything else in it is:

```formula essential
A_base = P − o_P
A_T = A_base + o_T
where
A_base: the base address, where the library's mapping starts in this process
P: the leaked pointer value, an address inside that library
o_P: the known offset of the leaked pointer's target from the library start, read from the same build
A_T: the address of another target the attacker wants, such as a useful function
o_T: that target's known offset from the library start
In words: subtract the leaked item's known offset to find where the library starts, then add another known offset to locate that target in the same mapping.
```

With illustrative numbers: a leaked pointer `0x7f12345a1b20` whose target is known to sit at offset `0x2db20` gives the base `0x7f1234574000`, and a target at offset `0x50d70` is then at `0x7f12345c4d70`. The base ends in three hexadecimal zeros, consistent with a 4 KiB (4,096-byte) page boundary; the sizes of memory pages and mapping alignments depend on the platform.

> [!analogy] Real-world analogy: a terrace of houses moved as one block
> Imagine a builder who places an identical terrace of houses somewhere different on every new estate, but always in the same order with the same spacing. Learn the address of one house whose position in the terrace you know, and you can work out every other house in that terrace.
>
> **How it maps:** The terrace is a library mapping, its random position is the ASLR base, and the fixed order and spacing are the offsets from that build. The one known house is the leaked pointer.
>
> **Where it stops:** Knowing one terrace says nothing about a separate terrace elsewhere on the estate (another mapping, such as the stack or heap, with its own random base), or about a terrace built to a different plan (an unknown library build).

Limits of what a leak gives:

- It reveals one mapping. Unrelated mappings and unknown builds stay hidden.
- Some objects are allocated separately or functions are resolved dynamically, so a symbol name alone does not prove that its run-time address has this simple relationship.
- A leak is information, not control. It does not disable NX or canaries, and the attacker still needs a separate bug that corrupts memory.

## Not every mapping is randomised

Conventional non-PIE ELF executables have fixed main-code addresses, so their code is a known target even with ASLR on. PIE permits random placement when the loader and OS enable it; compiler flags alone are not proof of effective randomisation. On Linux, `readelf -h` reports a PIE binary's type as `DYN` and a non-PIE executable's as `EXEC`.

Linux can randomise its kernel base when **KASLR** is supported and enabled. A known-offset kernel pointer leak can weaken that protection in the same way.

## Key takeaways
- Subtract a known pointer offset to recover the base of that known library mapping.
- Knowing one mapping does not reveal every other mapping or disable NX and canaries.
- PIE enables random placement of main code when the loader and OS actually apply it.

## Further reading
- [Linux virtual-memory sysctls](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [ELF program format — Linux manual](https://man7.org/linux/man-pages/man5/elf.5.html)
- [Instrumentation options — GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
