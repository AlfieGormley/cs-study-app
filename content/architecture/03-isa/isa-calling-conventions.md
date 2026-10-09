---
id: isa-calling-conventions
title: Calling conventions and stack frames
level: intermediate
minutes: 15
summary: How call and return work on x86-64 and ARM64, where arguments and return values go, which registers survive a call, and how stack frames, alignment and frame pointers fit together.
---

A function compiled today by Clang must be callable from code compiled years ago by GCC, from Rust, from Go via cgo, or from a hand-written assembly routine. That only works if everyone agrees on the details: where the arguments go, where the result comes back, which registers a call may destroy, and how the stack is laid out.

That agreement is the **calling convention**, part of a platform's **ABI** (application binary interface). The ABI also covers type sizes, struct layout and how system calls are made. Break the convention and you get crashes that look impossible: a variable that changes "by itself" across a call, or a segfault inside `printf`.

## Call and return

The hardware mechanism differs between the two ISAs.

**x86-64** keeps the return address on the stack:

- `call f` pushes the address of the next instruction (moves `rsp` down 8 bytes, then stores it) and jumps to `f`.
- `ret` pops that address into `rip`.

```formula
rsp_call = rsp − 8
rsp_ret = rsp_call + 8 = rsp
where
rsp: the stack pointer just before the call: the address of the current top of the stack
rsp_call: the stack pointer after call has pushed the return address
rsp_ret: the stack pointer after ret has popped it again
8: a return address is 64 bits = 8 bytes
In words: the stack grows towards lower addresses, so pushing subtracts 8 and popping adds the same 8 back; if rsp was 0x1000 before the call, it is 0xff8 inside the function and 0x1000 again after the return.
```

**ARM64** keeps it in a register:

- `bl f` (branch with link) puts the return address in `x30`, the **link register**, and jumps.
- `ret` branches to the address in `x30`.

The ARM64 design makes calls to **leaf functions** (functions that call nothing) cheap: no automatic return-address stack access from `bl`/`ret` themselves; the function can still access memory. But a function making a nested call and later returning to its own caller must preserve its original return address, or the inner `bl` will overwrite it and the outer `ret` will go to the wrong place.

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

## Stack frames

When a function needs stack storage, its **stack frame** is the region of stack holding its return address, saved registers, local variables, and outgoing arguments. The stack grows **downwards** (towards lower addresses) on both ISAs.

### A recursive example

```
long fact(long n) {
    return n <= 1 ? 1 : n * fact(n - 1);
}
```

Compilers may replace this recursion with a loop. The examples below deliberately retain recursion. With 64-bit signed `long`, use inputs at most 20 for a representable factorial; the original C multiplication has undefined behaviour on signed overflow. The limit comes from comparing factorials with the largest signed 64-bit value:

```formula
L_max = 2^63 − 1 ≈ 9.22 × 10^18
20! ≈ 2.43 × 10^18 < L_max
21! ≈ 5.11 × 10^19 > L_max
where
L_max: the largest value a 64-bit signed long can store; in two's complement the top bit carries the sign, so the positive range stops at 2^63 − 1
!: factorial: n! = n × (n − 1) × … × 1, so 3! = 6
n: any whole number 1 or more
…: and so on, through every whole number in between
≈: approximately equal to
<, >: less than, greater than
In words: 20 factorial still fits in a signed 64-bit integer, but 21 factorial is more than five times too big.
```

`n` must survive the recursive call, so it goes in a callee-saved register.

```
# long fact(long n)
fact:
    push  rbx          # save callee-saved
    mov   rbx, rdi     # keep n across call
    mov   eax, 1
    cmp   rdi, 1
    jle   .Lret        # n <= 1: return 1
    lea   rdi, [rdi - 1]
    call  fact         # rax = fact(n-1)
    imul  rax, rbx     # rax = n * rax
.Lret:
    pop   rbx
    ret
```

```
// long fact(long n)
fact:
    stp   x29, x30, [sp, #-32]!
    mov   x29, sp
    str   x19, [sp, #16]   // callee-saved
    mov   x19, x0          // keep n
    mov   x0, #1
    cmp   x19, #1
    b.le  .Lret            // n <= 1
    sub   x0, x19, #1
    bl    fact             // x0 = fact(n-1)
    mul   x0, x0, x19
.Lret:
    ldr   x19, [sp, #16]
    ldp   x29, x30, [sp], #32
    ret
```

The ARM64 prologue pushes `x29` and `x30` as a pair with a pre-indexed store, sets `x29` to point at that pair (the **frame record**), then saves `x19`. The epilogue reverses it. The x86 version has no frame pointer at all, which is normal for optimised code.

Here is the x86-64 stack while `fact(1)` runs, called as `fact(3)` from `main`. `S` is `rsp` on entry to `fact(3)`:

```
addr   contents
S      return addr into main
S-8    main's rbx (saved)
S-16   return addr into fact(3)
S-24   saved rbx = 3
S-32   return addr into fact(2)
S-40   saved rbx = 2    <- rsp in fact(1)
```

Each level costs 16 bytes: a return address and one saved register.

```formula
D = 16 × L
D = 16 × 3 = 48 bytes
where
D: the stack space used by the active fact calls, in bytes
L: how many fact calls are active at once (here fact(3), fact(2) and fact(1))
16: one 8-byte return address plus one 8-byte saved rbx per call
bytes: the unit of memory size; one byte is 8 bits
In words: stack use grows in a straight line with recursion depth; the three levels above fill the 48 bytes from S + 7 down to S − 40.
```

Unbounded recursion keeps adding frames until stack resources are exhausted. Stack limits and guard arrangements depend on the OS and thread configuration; Linux can signal `SIGSEGV` on stack exhaustion. No universal 8 MB default is assumed.

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

That is why `fact` above is aligned: its single `push rbx` moves `rsp` down another 8 bytes, to 4080 in this example, a multiple of 16 for the inner call. Compilers sometimes `push rax` or `sub rsp, 8` purely to fix alignment. Get it wrong in hand-written code and you may crash in a library function that uses aligned SSE instructions such as `movaps`.

ARM64 is stricter: `sp` itself must be 16-byte aligned whenever it is used as the base of a memory access (the hardware can trap if it is not), which is why registers are saved in pairs or in 16-byte blocks.

**Red zone.** The System V x86-64 ABI promises that the 128 bytes below `rsp` will not be clobbered by signal handlers. Leaf functions can use that space for locals without adjusting `rsp`. Kernel code is compiled with `-mno-red-zone` because hardware interrupts push data onto the current stack.

## Real-world variations

- **Windows x64** uses a different convention: arguments in `rcx`, `rdx`, `r8`, `r9`; the caller must reserve 32 bytes of "shadow space" on the stack (one 8-byte slot for each of the four register arguments); `rsi` and `rdi` are callee-saved, as are `xmm6`–`xmm15`. Code that crosses the boundary (Wine, JITs, hand-written assembly) must translate.
- **Variadic functions** on System V set `al` to a maximum (0–8) for the number of vector registers used; it need not be the exact count. This lets the callee decide whether to save vector argument registers. On Apple ARM64, anonymous variadic arguments go on the stack (named fixed parameters follow their normal rules), which breaks code that pretends a variadic function is non-variadic.
- **Tail calls.** If a function's last action is a call, the compiler can restore its frame and `jmp` (x86) or `b` (ARM64) to the target instead. The callee returns straight to the original caller, without adding another outstanding return frame; the callee may still use stack space. ABI and language constraints determine whether this transformation is possible.
- **Profiling and unwinding.** Frame pointers simplify walking a compatible chain, while unwind metadata can describe optimized frames without one. A universal performance percentage and blanket claims about distribution package rebuilds are omitted because they require version- and workload-specific evidence.

## Pitfalls

- **Assuming a scratch register survives a call.** After `call`, `rax`, `rcx`, `rdx`, `rsi`, `rdi` and `r8`–`r11` may hold anything.
- **Forgetting to save `x30`** across a nested ARM64 call that must return normally, so `ret` jumps back into the function itself.
- **Misaligning the stack** in hand-written x86-64 code, which crashes deep inside a library.
- **Using the Linux convention on Windows**, or vice versa, when writing assembly or declaring foreign functions.
- **Mismatched prototypes.** Calling a function through the wrong signature (for example passing an `int` where a `double` is expected) puts the value in the wrong register class entirely.

## Key takeaways
- `call`/`ret` use the stack for the return address on x86-64; `bl`/`ret` use the link register `x30` on ARM64.
- System V x86-64 passes integer arguments in `rdi, rsi, rdx, rcx, r8, r9`; AAPCS64 in `x0`–`x7`; results come back in `rax` or `x0`.
- Callee-saved registers (`rbx`, `rbp`, `r12`–`r15`; `x19`–`x28`) must be restored by the called function; consult the ABI tables for other preserved registers and machine state; “everything else” is too broad.
- A stack frame holds the return address, saved registers and locals; frame pointers chain frames together for debuggers and profilers.
- The stack must be 16-byte aligned at calls; aggregates classified for indirect return use a hidden pointer (`rdi` or `x8`); Windows x64 uses a different convention.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
