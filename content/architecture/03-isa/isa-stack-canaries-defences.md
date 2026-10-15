---
id: isa-stack-canaries-defences
title: Stack canaries and layered binary hardening
level: advanced
minutes: 5
sourceLesson: isa-compile-link-load
summary: Trace a protected stack layout and compare the scope of binary mitigations.
---

### Stack canaries: detect the overwrite

A **stack canary** (or stack protector) is a random value placed between a function's local buffers and its saved registers and return address. Before returning, the function checks it is unchanged. In a protected layout, a contiguous overwrite toward the return address crosses the guard. Detection requires that it actually change the guard and that execution reach a check.

Here is an illustrative x86-64 Linux/glibc stack-protector layout for a 32-byte local buffer. The ellipsis marks omitted application code; exact compiler output and layout vary:

```
greet:
    push  rbx
    sub   rsp, 48
    mov   rsi, rdi
    mov   rax, qword ptr fs:[40]
    # Save this thread’s guard in the frame.
    mov   qword ptr [rsp + 40], rax
    ...                   # use buf
    mov   rax, qword ptr fs:[40]
    cmp   rax, qword ptr [rsp + 40]
    # Abort if the stored guard changed.
    jne   .Lfail
    add   rsp, 48
    # Restore the caller’s saved register.
    pop   rbx
    ret
.Lfail:
    call  __stack_chk_fail@PLT
```

```
rsp+56  return address
rsp+48  saved rbx
rsp+40  canary
rsp+32  (padding)
rsp+0   buf[32]
```

The offsets follow from the prologue: `sub rsp, 48` reserves the buffer, padding and canary, and the earlier `push rbx` sits just above them.

```formula
r = F + 8
r = (32 + 8 + 8) + 8 = 56
where
r: how far above rsp the return address is, in bytes
F: the bytes reserved by `sub rsp, 48`: a 32-byte buffer, 8 bytes of padding and the 8-byte canary
8: the saved rbx, pushed before the subtraction
In words: the return address sits just above everything the function pushed or reserved, 56 bytes above rsp.
```

- In the glibc 2.39 x86-64 layout reviewed here, the stack guard is accessed in thread-local storage at `fs:0x28` (40). It is chosen at start-up from the kernel-supplied random bytes, with its lowest byte forced to zero to impede string-based disclosure and overwrite across the guard. A terminating zero can still overwrite its first byte unchanged; this is not protection against every overwrite or information leak.
- `__stack_chk_fail` prints "stack smashing detected" and aborts. A crash is a far better outcome than a hijack.
- `-fstack-protector-strong` covers additional functions with local arrays or references to local frame addresses; optimized-away or register-only objects do not count. Defaults depend on compiler and build configuration. `-fstack-protector-all` instruments every function at a higher cost.

Limits: a canary detects a mismatch when its check executes. A non-contiguous write that hits the canary may also be detected; writes that bypass it or cause harm before the check can escape that protection. A bug that writes to an arbitrary address, overwrites a function pointer among the locals, or first leaks the canary can avoid it. Forked children inherit the parent's canary.

## Defence in depth

| Mitigation | Stops | Weakness |
|---|---|---|
| NX / W^X | execution from protected data mappings | executable mappings and code reuse |
| ASLR + PIE | hard-coded addresses | info leaks |
| Canaries | some overwrites crossing the guard | arbitrary writes |
| Full RELRO | GOT overwrites | other pointers |

Additional mechanisms can reduce particular attack paths when hardware, OS, compiler and application support them. Intel CET adds a **shadow stack** (a protected copy of return addresses checked by ordinary near returns when shadow stacks are enabled) and indirect-branch tracking. AArch64 can provide **pointer authentication** (PAC, authenticating signed pointers such as return addresses) and **branch target identification** (BTI). When enabled, these mechanisms have architecture-specific rules and limits; BTI admits compatible landing instructions, which can include appropriate PAC instructions, not only a literal BTI mnemonic. With a supporting libc and compiler configuration, `_FORTIFY_SOURCE` can add checks to selected library operations using inferred object sizes; it does not bounds-check every memory access.

Tools such as checksec (use the syntax documented for your installed version) summarise binary hardening indicators. `readelf -lW` and `readelf -d` expose segment permissions, GNU_RELRO and binding tags; symbol or instruction inspection can provide stack-protector evidence. Binary indicators do not prove that runtime hardware or OS enforcement is enabled for every mechanism.

## Pitfalls

- **Disabling mitigations "to make it work".** `-z execstack` or `-fno-stack-protector` in a build script usually hides a real bug.
- **Thinking ASLR makes leaks harmless.** Printing a pointer in an error message can defeat it for the whole module.
- **Library order** on the link line, and confusing `.a` with `.so` behaviour.
- **Assuming mitigations replace fixing bugs.** They raise the cost of exploitation; they don't remove the vulnerability.

## Key takeaways
- A canary only detects a changed guard when its check executes.
- The shown glibc guard layout and zero byte are platform-specific.
- NX, ASLR, canaries and RELRO protect different attack paths and have different limits.

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
