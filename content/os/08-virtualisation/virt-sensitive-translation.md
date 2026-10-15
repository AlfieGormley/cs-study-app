---
id: virt-sensitive-translation
title: Sensitive instructions and binary translation
level: basic
minutes: 3
sourceLesson: virt-hypervisors
summary: Trap-and-emulate needs to intercept sensitive operations; classic x86 did not meet the simple sufficient condition.
---

This unit focuses on sensitive instructions and binary translation. It builds on the earlier virtualisation units in this module.

## The Popek–Goldberg requirements

In 1974 Gerald Popek and Robert Goldberg formalised when trap-and-emulate works. A VMM must provide three properties:

- **Equivalence (fidelity).** A program behaves the same in the VM as on real hardware, apart from timing and resource availability.
- **Resource control (safety).** The VMM is in complete control of the real resources; a guest cannot grab memory or devices it was not given.
- **Efficiency property.** The vast majority of instructions run directly on the hardware, without VMM intervention.

They then split instructions into two groups:

- **Privileged**: traps if executed in user mode.
- **Sensitive instructions**: reads or changes machine configuration (control-sensitive), or behaves differently depending on the mode or location it runs in (behaviour-sensitive).

Their theorem gives a **sufficient condition**, within its formal machine model: a VMM can be constructed if every sensitive instruction is privileged. Then every instruction the VMM needs to see is guaranteed to trap.

> [!warning] x86 failed the test
> Robin and Irvine's 2000 Pentium analysis identified 17 instructions violating its trap-based virtualisation requirement. The infamous one is `POPF`. In kernel mode it can change the interrupt flag. In the conventional protected-mode case with CPL greater than IOPL (excluding virtual-8086 complications), it leaves IF unchanged without trapping merely because of that attempted change. A deprivileged guest kernel that runs `POPF` to re-enable interrupts gets no error and no trap; the hypervisor never finds out. Others, like `SGDT` and `SIDT`, let user code read where the *real* descriptor tables are, revealing the hypervisor.

Because some instructions never trapped, pure trap-and-emulate on x86 was impossible. Two important software approaches made x86 virtualisation work anyway.

## Workaround 1: binary translation

VMware's 1999 product scanned guest **kernel** code just before running it, a basic block at a time, and rewrote it into a **translation cache**:

- Most instructions are copied unchanged ("identical" translation).
- Problem instructions like `POPF` are replaced with short sequences that call into the VMM or update the virtual CPU directly.
- Translated blocks are cached and chained together, so hot kernel code is translated once and reused.

Guest **user** code normally ran directly at its expected privilege level, with the VMM controlling memory and handling traps as needed. This avoids translating the application instruction stream; it does not imply every observable machine detail or timing is identical.

Binary translation needs no changes to the guest, so it runs unmodified Windows. It is complex, though: self-modifying code, precise exceptions and translating indirect jumps are all fiddly. Surprisingly, it was fast. A 2006 VMware paper (Adams and Agesen) found the first generation of hardware support was often *slower* than mature binary translation, because hardware traps were so expensive.

## Key takeaways

- Trap-and-emulate needs to intercept sensitive operations; classic x86 did not meet the simple sufficient condition.
- Binary translation rewrites troublesome guest-kernel instructions and caches the result.

## Further reading

- [Formal requirements — Popek and Goldberg (1974, PDF)](https://www.cs.columbia.edu/~cdall/candidacy/pdf/Popek.pdf)
- [Software and hardware virtualisation — Adams and Agesen (2006, PDF)](https://iitd-plos.github.io/col718/ref/asplos235_adams.pdf)
- [Virtual Machine Monitors — OSTEP appendix (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vmm-intro.pdf)
- [Popek and Goldberg virtualization requirements — Wikipedia](https://en.wikipedia.org/wiki/Popek_and_Goldberg_virtualization_requirements)
- [Xen and the Art of Virtualization (SOSP 2003, PDF)](https://www.cl.cam.ac.uk/research/srg/netos/papers/2003-xensosp.pdf)
- [Hypervisor — Wikipedia](https://en.wikipedia.org/wiki/Hypervisor)
- [x86 virtualization — Wikipedia](https://en.wikipedia.org/wiki/X86_virtualization)
