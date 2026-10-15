---
id: isa-call-return-state
title: Calls, returns and the link register
level: intermediate
minutes: 3
sourceLesson: isa-calling-conventions
summary: Trace the different return-address mechanisms and why nested calls need saved state.
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

## Key takeaways
- An ABI lets separately compiled code agree on machine-level interfaces.
- x86 CALL saves the return address on the stack.
- A64 BL overwrites X30; a nested ordinary return needs the original address preserved.

## Further reading
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [System V x86-64 psABI — GitLab](https://gitlab.com/x86-psABIs/x86-64-ABI)
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [x64 calling convention — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
- [The return of the frame pointers — Brendan Gregg](https://www.brendangregg.com/blog/2024-03-17/the-return-of-the-frame-pointers.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)

- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)
