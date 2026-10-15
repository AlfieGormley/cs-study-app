---
id: isa-recursive-stack-frames
title: Trace recursive factorial stack frames
level: intermediate
minutes: 4
sourceLesson: isa-calling-conventions
summary: Trace the recursive factorial implementations and account for each saved stack slot.
---

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
    # Base case returns one.
    mov   eax, 1
    cmp   rdi, 1
    jle   .Lret        # n <= 1: return 1
    lea   rdi, [rdi - 1]
    call  fact         # rax = fact(n-1)
    imul  rax, rbx     # rax = n * rax
.Lret:
    # Restore the caller’s saved register.
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

For this exact x86 listing, each active level costs 16 bytes: a return address and one saved register. The A64 listing reserves 32 bytes per active level; its return address is saved inside that allocation. Neither size is an ISA-wide recursion cost.

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

## Key takeaways
- A recursive call must preserve the input needed after it returns.
- The examples restore saved registers and the return state.
- Stack use grows with active call depth; signed factorial also has a representable range.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
