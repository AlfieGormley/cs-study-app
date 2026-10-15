---
id: isa-register-preservation
title: Caller-saved and callee-saved registers
level: intermediate
minutes: 3
sourceLesson: isa-calling-conventions
summary: Choose a register that survives a call and understand who must restore it.
---

A caller transfers control to a callee and expects to continue after its return. Register-preservation rules decide which values remain valid at that point.

## Who saves which registers

A call may destroy some registers and must preserve others:

- **Caller-saved** (also called volatile registers or scratch registers): the called function may overwrite them freely. If the caller needs a value in one of these after the call, the caller must save it.
- **Callee-saved** (also called non-volatile registers): the called function must restore them before returning. If it wants to use one, it saves the old value in its prologue and restores it in its epilogue.

| | System V x86-64 | AAPCS64 |
|---|---|---|
| Callee-saved | `rbx rbp r12`–`r15`, restored `rsp` | `x19`–`x28`, `x29`, `sp` |
| Caller-saved | `rax rcx rdx rsi rdi r8`–`r11` | `x0`–`x17`, `x30` |
| Vector callee-saved | none | low 64 bits of `v8`–`v15` |

Some ARM64 registers have special jobs. `x8` passes the large-struct return pointer. `x16` and `x17` are scratch registers that linker-generated stubs may overwrite. `x18` is the **platform register**, reserved on Apple platforms and Windows. Portable code should not touch it.

Why have both kinds? If every register were caller-saved, every call site would spill everything it cared about. If every register were callee-saved, every function would save registers it uses even when no caller needs them. A split lets the compiler put short-lived values in scratch registers and values live across calls in callee-saved ones.

## Key takeaways
- Caller-saved values need preservation if the caller still needs them.
- A callee restores any callee-saved registers it changes.
- A64 platform and linker-scratch registers have additional rules.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
