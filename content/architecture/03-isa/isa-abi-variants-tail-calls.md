---
id: isa-abi-variants-tail-calls
title: Windows, variadic calls and tail-call boundaries
level: intermediate
minutes: 3
sourceLesson: isa-calling-conventions
summary: Recognise platform differences and the conditions behind tail-call and unwind behaviour.
---

## Real-world variations

- **Windows x64** uses a different convention: arguments in `rcx`, `rdx`, `r8`, `r9`; the caller must reserve 32 bytes of "shadow space" on the stack (one 8-byte slot for each of the four register arguments); `rsi` and `rdi` are callee-saved, as are `xmm6`–`xmm15`. Code that crosses the boundary (Wine, JITs, hand-written assembly) must translate.
- **Variadic functions** on System V set `al` to a maximum (0–8) for the number of vector registers used; it need not be the exact count. This lets the callee decide whether to save vector argument registers. On Apple ARM64, anonymous variadic arguments go on the stack (named fixed parameters follow their normal rules), which breaks code that pretends a variadic function is non-variadic.
- **Tail calls.** If a function's last action is a call, the compiler can restore its frame and `jmp` (x86) or `b` (ARM64) to the target instead. The callee returns straight to the original caller, without adding another outstanding return frame; the callee may still use stack space. ABI and language constraints determine whether this transformation is possible.
- **Profiling and unwinding.** Frame pointers simplify walking a compatible chain, while unwind metadata can describe optimized frames without one. A universal performance percentage and blanket claims about distribution package rebuilds are omitted because they require version- and workload-specific evidence.

## Pitfalls

- **Assuming a scratch register survives a call.** After `call`, `rax`, `rcx`, `rdx`, `rsi`, `rdi` and `r8`–`r11` may hold anything.
- **Forgetting to save `x30`** across a nested ARM64 call that must return normally, so `ret` jumps back into the function itself.
- **Misaligning the stack** in hand-written x86-64 code, which can cause a fault in a library using aligned instructions.
- **Using the Linux convention on Windows**, or vice versa, when writing assembly or declaring foreign functions.
- **Mismatched prototypes.** Calling a function through the wrong signature (for example passing an `int` where a `double` is expected) puts the value in the wrong register class entirely.

## Key takeaways
- Windows x64 uses different argument registers and shadow space.
- Variadic arguments need the platform’s special rules.
- An eligible tail call restores the frame and transfers to the next callee.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
