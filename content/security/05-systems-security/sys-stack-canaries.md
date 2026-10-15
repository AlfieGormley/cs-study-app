---
id: sys-stack-canaries
title: What a stack canary can detect
level: intermediate
minutes: 5
sourceLesson: sys-mitigations
summary: A canary guards particular protected stack exits and layouts; it is not a bounds check.
---

Memory-unsafe operations can leave exploitable bugs in a program. Compilers, operating systems and CPUs provide **exploit mitigations** that restrict particular ways of abusing them. Their effectiveness depends on the enabled features and the program.

A mitigation does not repair the faulty source operation. It may prevent exploitation or terminate the process, but a crash is still an availability/security failure. A program may also leak information or corrupt sensitive data before a check fires. Some attacks need several vulnerabilities; there is no universal minimum chain length.

## The attacker's checklist

A classic control-flow attack may corrupt a return address or function pointer, determine a useful destination and redirect execution there. Other attacks change data, such as an authorisation flag, without these steps.

The mitigations below address different parts of that process. None covers every possible memory-safety failure.

## Stack canaries

A **stack canary** is a guard value checked by compiler-generated code on protected function exits. A common downward-growing stack layout places it between buffers and the saved return address, as illustrated below; exact layout and which functions are protected depend on the ABI, compiler and optimisation.

```
higher addresses
+---------------------+
| return address      |
| saved frame pointer |
| CANARY (random)     |  <- checked at exit
| char buf[64]        |  <- overflow goes up
| other locals        |
+---------------------+
lower addresses
```

In the illustrated layout, a linear overflow from `buf` must pass through the canary to reach the return address. If the value has changed, the program calls `__stack_chk_fail` and aborts instead of returning.

Details that matter:

- In the inspected glibc implementation, startup randomness initializes the guard and its first byte in memory is cleared. On little-endian x86-64 this is the lowest byte. A NUL-terminated copy cannot both preserve that byte and continue past it; the destination NUL does **not** itself stop an overflowing copy.
- GCC `-fstack-protector-strong` covers local arrays and references to local frame addresses, considering variables that actually remain on the stack after optimisation.
- Do not rely on a universal ordering of other locals or assume every function is protected.

How hard is the canary to guess blindly? On x86-64 the glibc guard is one 8-byte machine word, and the cleared byte leaves seven random bytes:

```formula
b = (8 × 8) − 8 = 56
N = 2^b = 2^56 ≈ 7.2 × 10^16
p = 1 / N
where
b: the number of unpredictable bits in the canary
8 × 8: the canary's 8 bytes of 8 bits each, one 64-bit word on x86-64
8: subtracted for the 8 bits of the byte glibc sets to zero, which an attacker already knows
N: the number of equally likely canary values
2^b: b copies of 2 multiplied together; each random bit doubles the number of possible values
≈: approximately equal to
10^16: 16 copies of 10 multiplied together, ten thousand million million
p: the chance that one blind guess of the whole canary is right
In words: with 56 random bits there are about 72 thousand million million possible canaries, so a single blind guess has a very small chance under this model.
```

A canary leak can avoid that blind-guessing problem. One important exception: a forked child process gets a copy of its parent's memory, canary included, so children initially inherit that guard unless the runtime changes it or they execute a new process image. If a wrong guess merely crashes one child, an attacker who can overwrite just the next canary byte, and see whether the child crashed, learns the bytes one at a time:

```formula
G_max = k × 2^8
G_max = 7 × 256 = 1,792
where
G_max: the worst-case number of guesses to recover all the random bytes, one byte at a time
k: the number of unknown canary bytes, 7 here
2^8: 256, the number of values one 8-bit byte can take
In words: guessing byte by byte needs at most 256 tries for each of the 7 bytes, about 1,800 in all, instead of 2^56 for the whole value at once.
```

This byte-by-byte method was used against forking servers in the Blind ROP research (Bittau et al., 2014).

What canaries don't stop: heap overflows, overwrites of other data *before* the function returns (such as a function pointer used inside it), overwrites confined to fields within a struct (field order is fixed by the language), and attacks where a separate bug leaks the canary's value first.

## Key takeaways
- A canary guards particular protected stack exits and layouts; it is not a bounds check.
- The glibc x86-64 example clears one guard byte, leaving seven random bytes under the stated model.
- A leak, a write that skips the guard or a data decision before exit can defeat the intended protection.

## Further reading
- [Instrumentation options — GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
- [glibc guard initialisation](https://codebrowser.dev/glibc/glibc/sysdeps/generic/dl-osinfo.h.html)
- [Hacking Blind — original paper](https://www.scs.stanford.edu/brop/bittau-brop.pdf)
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
