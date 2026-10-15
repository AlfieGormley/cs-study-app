---
id: isa-argument-return-abi
title: Argument registers, stack arguments and struct returns
level: intermediate
minutes: 4
sourceLesson: isa-calling-conventions
summary: Place ordinary arguments and aggregate results under the two platform ABIs.
---

A calling convention fixes how values cross a function-call boundary. The following examples compare ordinary scalar System V AMD64 and base AAPCS64 calls; platform extensions need their own rules.

## Where arguments and results go

On Linux, macOS and the BSDs, x86-64 uses the **System V AMD64 ABI**. Linux AArch64 uses **AAPCS64**; Apple’s ARM64 ABI has material differences, particularly for variadic and stack arguments. The table covers common fixed scalar parameters, not every ABI type.

| | System V x86-64 | AAPCS64 |
|---|---|---|
| Integer/pointer args | `rdi rsi rdx rcx r8 r9` | `x0`–`x7` |
| Float/double args | `xmm0`–`xmm7` | `v0`–`v7` |
| Integer return | `rax` (+ `rdx`) | `x0` (+ `x1`) |
| Float return | `xmm0` | `v0` |
| Further args | on the stack | on the stack |

Integer and floating-point arguments are counted separately. For `double f(double x, int n)`, `x` arrives in `xmm0` and `n` in `edi` (on ARM64: `d0` and `w0`).

### More than six (or eight) arguments

Here is a call to an eight-argument function `g(1, 2, ..., 8)`, in a representative System V x86-64 sequence. Assume `rsp` is already 16-byte aligned at the start of this fragment:

```
    mov   edi, 1
    mov   esi, 2
    mov   edx, 3
    mov   ecx, 4
    mov   r8d, 5
    mov   r9d, 6
    push  8          # 8th arg
    push  7          # 7th arg (lowest)
    call  g
    add   rsp, 16    # caller pops args
```

Arguments 7 and 8 go on the stack, pushed in reverse so the 7th ends up at the lower address. On entry to `g`, the return address is at `[rsp]` and the stack arguments sit just above it:

```formula
A_k = rsp + 8 × (k − 6)   for k ≥ 7
A_7 = rsp + 8 × 1 = rsp + 8
A_8 = rsp + 8 × 2 = rsp + 16
where
A_k, A_7, A_8: the address of argument number k (7 and 8 here), as seen on entry to g
k: the argument's position in the call, counting from 1
rsp: the stack pointer on entry to g, which points at the return address
6: the first six integer arguments travel in registers (rdi, rsi, rdx, rcx, r8, r9), so the 7th is the first on the stack
8: each stack argument slot is 8 bytes
≥: greater than or equal to
In words: skip the 8-byte return address, then each later argument is a further 8 bytes up; after the call, the caller frees the two slots with `add rsp, 16` (2 × 8 bytes).
```

This assumes each stack argument fits one 8-byte slot, as these `int`s do; larger aggregates take more. On ARM64, all eight fit in `x0`–`x7`.

### Returning structs

Aggregate returns depend on ABI classification, not size alone:

- Under System V AMD64, many ordinary aggregates up to 16 bytes return in integer and/or vector registers. Unaligned fields and other classification rules can force memory return even for small aggregates; supported vector-shaped aggregates have additional exceptions.
- Under base AAPCS64, ordinary non-homogeneous composites up to 16 bytes can use `x0`/`x1`. Homogeneous floating-point aggregates of up to four members can use vector registers even when larger than 16 bytes.
- For an indirect return, the caller supplies storage. System V passes its address in `rdi`, consuming an integer argument slot, and returns that address in `rax`. AAPCS64 uses `x8`, leaving the normal argument registers available. Consult the full ABI for complex/vector types and C++ objects.

## Key takeaways
- Integer and floating-point arguments use separate allocation rules.
- Further ordinary integer arguments occupy stack slots.
- Indirect aggregate returns use RDI in System V and X8 in base AAPCS64.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
