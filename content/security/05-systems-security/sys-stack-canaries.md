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

In the illustrated layout, a linear overflow from `buf` must pass through the canary to reach the return address. If the value has changed, the program calls `__stack_chk_fail` and aborts instead of returning. With glibc 2.31 or later the process prints `*** stack smashing detected ***: terminated` (older versions also printed the program name) and is killed by `SIGABRT`; that is what a 40-character name passed to the `greet` example from the buffer-overflow lesson produced in GCC 13 and GCC 14 test builds with `-fstack-protector-strong`. Adding `-D_FORTIFY_SOURCE=3` changed the message to `*** buffer overflow detected ***`, because glibc's checked `strcpy` caught the copy before the function returned. The abort shows that a protected frame was corrupted. It does not say where the bug is, and the overflow still needs fixing.

> [!analogy] Real-world analogy: a seal across a door
> A guard puts a numbered paper seal across a storeroom door and checks it on every round. Anyone forcing the door from the corridor must tear the seal, and the next round raises the alarm.
>
> **How it maps:** The door is the saved return address, the seal is the canary placed in front of it, and the guard's round is the check on a protected function exit. Forcing the door from the corridor is a linear overflow that has to cross the canary.
>
> **Where it stops:** The seal says nothing about a thief who learned its number and printed a copy (a canary leak), climbed in through a window (a write that skips the canary), or took something before the next round (data used before the function returns). Real canaries are also checked only at protected exits, not continuously.

Details that matter:

- In the inspected glibc implementation, startup randomness initializes the guard and its first byte in memory is cleared. On little-endian x86-64 this is the lowest byte. A NUL-terminated copy cannot both preserve that byte and continue past it; the destination NUL does **not** itself stop an overflowing copy.
- GCC `-fstack-protector-strong` covers local arrays and references to local frame addresses, considering variables that actually remain on the stack after optimisation.
- Do not rely on a universal ordering of other locals or assume every function is protected.

How hard is the canary to guess blindly? On x86-64 the glibc guard is one 8-byte machine word, and the cleared byte leaves seven random bytes, 56 random bits. A single blind guess of the whole value is right only about once in 72 thousand million million tries, and each wrong guess normally aborts the process.

A canary leak avoids that guessing problem entirely. So can one important exception: a forked child process gets a copy of its parent's memory, canary included, so children initially inherit that guard unless the runtime changes it or they execute a new process image. If a wrong guess merely crashes one child, an attacker who can overwrite just the next canary byte, and see whether the child crashed, learns the bytes one at a time: at most 256 tries per byte, under 1,800 tries for all seven.

```formula reference
N_whole = 2^56 ≈ 7.2 × 10^16
G_bytes ≤ 7 × 2^8 = 1,792
where
N_whole: the number of possible values for the canary's 7 random bytes guessed all at once
2^56: 56 copies of 2 multiplied together; each random bit doubles the number of possible values
≈: approximately equal to
10^16: 16 copies of 10 multiplied together, ten thousand million million
G_bytes: the worst-case number of tries when a crash or no-crash answer reveals each byte separately
7: the number of unknown canary bytes
2^8: 256, the number of values one 8-bit byte can take
≤: at most
In words: guessing the whole canary at once means one chance in roughly 72 thousand million million per try, but if each byte can be tested on its own, the attacker needs at most 256 tries for each of the 7 bytes, under 1,800 in all.
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
