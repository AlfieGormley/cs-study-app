---
id: isa-stack-alignment-red-zone
title: Frame pointers, call alignment and the red zone
level: intermediate
minutes: 3
sourceLesson: isa-calling-conventions
summary: Calculate argument offsets and alignment and identify where the red zone applies.
---

The preceding recursive factorial saved RBX with a single push before calling itself. The following examples use System V x86-64 unless a sentence explicitly names AArch64.

### The classic frame-pointer prologue

A classic frame-pointer prologue uses `rbp` as a fixed reference point. Compiler options and target rules determine which functions actually retain frame pointers:

```
# long f(long x), -O0 style
f:
    push  rbp          # save caller's rbp
    mov   rbp, rsp     # rbp = frame base
    sub   rsp, 32      # room for locals
    mov   qword ptr [rbp - 8], rdi  # x
    mov   rax, qword ptr [rbp - 8]
    leave              # rsp = rbp, pop rbp
    ret
```

When callers and callees maintain compatible frame records, saved `rbp` values form a linked list through their frames. Debuggers and profilers walk it to produce a backtrace.

## Alignment and the red zone

**Alignment.** For the ordinary calls shown, both ABIs require 16-byte stack alignment at the call boundary. System V can require stronger alignment for some stack-passed over-aligned or vector arguments. On x86-64, `rsp` must be a multiple of 16 just *before* the `call`, so on entry to a function (after the 8-byte return address is pushed) it is 8 past a multiple of 16:

```formula
rsp_before mod 16 = 0
rsp_entry = rsp_before − 8
rsp_entry mod 16 = 8
rsp_entry = 4096 − 8 = 4088
4088 mod 16 = 8
where
rsp_before: the stack pointer just before the call instruction, in this example 4096 (0x1000)
rsp_entry: the stack pointer on the first instruction of the called function
mod: modulo: the remainder after dividing by 16 (4088 = 255 × 16 + 8)
16: the alignment in bytes that both ABIs require at a call
8: the size of the pushed return address
In words: the call's push leaves rsp 8 bytes off a 16-byte boundary, so a function must move rsp by another 8 (or 24, 40, …) before it makes its own call.
```

That is why the preceding factorial unit’s `fact` is aligned: its single `push rbx` moves `rsp` down another 8 bytes, to 4080 in this example, a multiple of 16 for the inner call. Compilers sometimes `push rax` or `sub rsp, 8` purely to fix alignment. Get it wrong in hand-written code and you may crash in a library function that uses aligned SSE instructions such as `movaps`.

ARM64 is stricter: `sp` itself must be 16-byte aligned whenever it is used as the base of a memory access (the hardware can trap if it is not), so stack allocations normally preserve that alignment. Saving a pair is convenient, but a single register can also be stored in an aligned allocation.

**Red zone.** The System V x86-64 ABI promises that the 128 bytes below `rsp` will not be clobbered by signal handlers. Leaf functions can use that space for locals without adjusting `rsp`. Kernel code is compiled with `-mno-red-zone` because hardware interrupts push data onto the current stack.

## Key takeaways
- A frame pointer offers a stable base when the function maintains one.
- Ordinary System V calls align RSP before CALL, which then pushes eight bytes.
- The System V user-space red zone is not a kernel interrupt-stack guarantee.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
