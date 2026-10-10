---
id: sys-mitigations
title: Exploit mitigations
level: intermediate
minutes: 13
summary: Stack canaries, DEP/NX, ASLR, RELRO, FORTIFY_SOURCE, control-flow integrity, shadow stacks and memory tagging, what each one stops and what it doesn't.
---

Memory-unsafe operations can leave exploitable bugs in a program. Compilers, operating systems and CPUs provide **exploit mitigations** that restrict particular ways of exploiting them. Their effectiveness depends on the enabled features and the program.

A mitigation does not repair the faulty source operation. It may prevent exploitation or terminate the process, but a crash is still an availability/security failure. A program may also leak information or corrupt sensitive data before a check fires. Some attacks need several vulnerabilities; there is no universal minimum chain length.

## The attacker's checklist

A classic control-flow attack may corrupt a return address or function pointer, determine a useful destination and redirect execution there. Other attacks change data, such as an authorization flag, without these steps.

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

A linear overflow from `buf` must pass through the canary to reach the return address. If the value has changed, the program calls `__stack_chk_fail` and aborts instead of returning.

Details that matter:

- In the inspected glibc implementation, startup randomness initializes the guard and its first byte in memory is cleared. On little-endian x86-64 this is the lowest byte. A NUL-terminated copy cannot both preserve that byte and continue past it; the destination NUL does **not** itself stop an overflowing copy.
- GCC `-fstack-protector-strong` covers local arrays and references to local frame addresses, considering variables that actually remain on the stack after optimisation.
- Do not rely on a universal ordering of other locals or assume every function is protected.

How hard is the canary to guess blindly? On x86-64 the glibc guard is one 8-byte machine word, and the cleared byte leaves seven random bytes:

```formula
b = 8 × 8 − 8 = 56
N = 2^b = 2^56 ≈ 7.2 × 10^16
p = 1 / N
where
b: the number of unpredictable bits in the canary
8 × 8: the canary's 8 bytes of 8 bits each, one 64-bit word on x86-64
8: subtracted for the 8 bits of the byte glibc sets to zero, which an attacker already knows
N: the number of equally likely canary values
2^b: 2 multiplied by itself b times; each random bit doubles the number of possible values
≈: approximately equal to
10^16: 10 multiplied by itself 16 times, ten thousand million million
p: the chance that one blind guess of the whole canary is right
In words: with 56 random bits there are about 72 thousand million million possible canaries, so one blind guess essentially never succeeds.
```

That is why attackers try to leak the canary instead. One important exception: a forked child process gets a copy of its parent's memory, canary included, so every child of a forking server shares one canary. If a wrong guess merely crashes one child, an attacker who can overwrite just the next canary byte, and see whether the child crashed, learns the bytes one at a time:

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

What canaries don't stop: heap overflows, overwrites of other data *before* the function returns (such as a function pointer used inside it), overflows within a struct (field order is fixed by the language), and attacks where a separate bug leaks the canary's value first.

## DEP / NX: data is not code

**DEP/NX** prevents instruction execution from pages marked non-executable. Write and execute permissions are separate: NX alone does not enforce **W^X**, the stronger policy that a page is never writable and executable simultaneously. The table illustrates common permissions, not a guarantee for every mapping.

| Region | Read | Write | Execute |
|---|---|---|---|
| Code (.text) | yes | no | yes |
| Stack | yes | yes | no |
| Heap | yes | yes | no |

An attempt to fetch instructions from a non-executable stack or heap page faults. Whether the process then terminates depends on OS handling. A process can have executable mappings, including code produced by a JIT compiler at run time; enabling DEP does not mean every data allocation is necessarily non-executable.

Attackers responded with **code-reuse** attacks: rather than injecting new code, they redirect control through short snippets of code that already exist in the program and its libraries, which are legitimately executable. The best-known form is **return-oriented programming** (ROP). Code reuse is why DEP alone is not enough, and why the attacker's "know where" step became so important.

JIT compilers generate executable code at run time. Their permission transitions and aliases need careful protection; a writable alias of executable storage can undermine the intended restriction. The exact mechanism is platform-specific.

## ASLR: hide the addresses

**Address space layout randomisation** varies placement of selected mappings, such as libraries and stacks, when a process image is loaded. Support and configuration determine which mappings vary. A forked child process normally inherits the existing address space. Wrong target guesses can fail or crash; neither outcome is guaranteed for every corruption.

How much it helps depends on **entropy**, the number of random bits. Each independent, uniformly random bit doubles the number of places a mapping can start:

```formula
N = 2^b
N = 2^8 = 256
N = 2^28 = 268,435,456
where
N: the number of equally likely positions (base addresses) the mapping can have
b: the bits of entropy: how many independent, uniformly random bits choose the position; 8 and 28 here
2^b: 2 multiplied by itself b times
In words: with 8 random bits a mapping has 256 possible positions; with 28 bits it has over 268 million.
```

These are teaching examples, not asserted Linux defaults. Architecture, kernel settings and distribution policy affect actual entropy. On supported Linux systems, `vm.mmap_rnd_bits` controls randomisation for relevant mappings.

An attacker without a leak must guess, and the average number of attempts depends on whether the base changes between attempts. If it stays fixed (forked workers inherit it, as above) and each wrong guess is ruled out, the right base is equally likely to be first, second and so on up to last:

```formula
E_fixed = (N + 1) / 2
E_fixed = (256 + 1) / 2 = 128.5
where
E_fixed: the expected (average) number of attempts until the right base is found, when the base stays fixed
N: the number of equally likely bases; 256 for 8 bits
1: added because the right base's position runs from 1 to N, and the average of 1, 2, …, N is (1 + N) / 2
In words: trying each of N possible fixed bases once finds the answer, on average, about halfway through the list.
```

If instead every attempt meets a freshly randomised base (for example, each attempt runs a newly executed process), no attempt rules anything out. Each try is a new 1-in-N chance, and the average number of tries is N:

```formula
p = 1 / N
E_new = 1 / p = N
E_new = 256
where
p: the chance that one attempt succeeds
N: the number of equally likely bases; 256 for 8 bits
E_new: the expected number of attempts when the base is re-randomised every time; this is the mean of a geometric distribution, which counts tries up to the first success
In words: with a fresh 1-in-256 chance each time, success takes 256 attempts on average.
```

With 28 bits the fixed-base model gives about 134 million attempts on average (268,435,457 / 2). Neither model says how long an attack takes: request rate, restart cost and monitoring decide that.

Two caveats make ASLR weaker than the numbers suggest:

1. **Leaks can weaken ASLR.** A pointer into a known library build at a known offset reveals that mapping base. It does not automatically reveal unrelated mappings or unknown builds.

Within one library build, every function and variable sits at a fixed distance (offset) from the library's start, which can be read from the library file. So one leaked pointer gives the whole mapping. With illustrative hexadecimal numbers:

```formula
A_base = P − o_P
A_base = 0x7f12345a1b20 − 0x2db20
A_base = 0x7f1234574000
A_T = A_base + o_T
A_T = 0x7f1234574000 + 0x50d70
A_T = 0x7f12345c4d70
where
A_base: the base address, where the library's mapping starts in this process
P: the leaked pointer value, an address inside that library
o_P: the known offset of the leaked pointer's target from the library start, read from the same build
A_T: the address of another target the attacker wants, such as a useful function
o_T: that target's known offset from the library start
0x7f12345a1b20: a hexadecimal (base-16) number, marked by the 0x prefix; the values here are made up for illustration
In words: subtract the leaked item's known offset to find where the library starts, then add any other offset to locate anything else in the same library.
```

ASLR moves the base, not the layout inside the library, which is why one leak is enough for that mapping. The base above ends in three hex zeros because mappings typically start on a 4 KiB page boundary (4,096 = 0x1000).

2. **Not every mapping is randomised.** Conventional non-PIE ELF executables have fixed main-code addresses. PIE permits random placement when the loader and OS enable it; compiler flags alone are not proof of effective randomisation.

Linux can randomise its kernel base when **KASLR** is supported and enabled. A known-offset kernel pointer leak can weaken that protection.

## RELRO and FORTIFY_SOURCE

Two more toolchain hardening features are common on Linux:

- **RELRO** makes a designated ELF relocation region read-only after relocation. In a conventional supported ELF toolchain, full RELRO (`-Wl,-z,relro,-z,now`) also resolves lazy function bindings at load time so the GOT can be protected. Later `dlopen` loads have their own relocations. This does not protect every function pointer in a program.
- **`_FORTIFY_SOURCE`** adds compile-time diagnostics and run-time checks to supported library calls where object-size information is available. Level 3 uses dynamic object-size information and requires a compatible compiler/libc; glibc enables these wrappers only with optimisation. Unknown sizes and unsupported operations can remain unchecked.

An illustrative GNU/Linux ELF build fragment follows. It requires toolchain support for level-3 fortification; the CET-related flag is for supported x86 targets. Check platform documentation and the resulting binary/runtime configuration. Accepting a compiler flag does not prove that hardware enforcement is active.

```
CFLAGS += -O2 -fstack-protector-strong \
  -D_FORTIFY_SOURCE=3 -fPIE \
  -fcf-protection=full
LDFLAGS += -pie -Wl,-z,relro,-z,now
```

## Control-flow integrity

**Control-flow integrity** constrains allowed control transfers. Different schemes cover different indirect calls, jumps or returns; they do not all check every transfer or enforce the same policy.

### Forward edges: indirect calls

An indirect call (`fp()`, a C++ virtual call) should only reach functions that could validly be called there.

- **Clang CFI** includes type-based indirect-call and virtual-call checks. Its `-fsanitize=cfi` family requires the documented LTO/visibility setup; that flag alone is not a complete build recipe.
- **Microsoft CFG** validates instrumented indirect calls against allowed targets; it is not a complete type-based policy.
- **Intel IBT** and **Arm BTI** constrain relevant indirect branches to suitable landing pads when enforcement is enabled. Landing-pad validation is coarser than checking the intended function type.

### Backward edges: returns

A **shadow stack** keeps protected return-address copies. With x86 CET shadow-stack enforcement, calls update the two stacks and returns check agreement. Linux user-space use requires supporting CPU, kernel, runtime and enablement; kernel availability alone does not protect every application.

**Pointer authentication** can protect selected Arm pointers with a keyed authentication code, incorporating contextual information. It authenticates rather than encrypts the pointer, and is not a general memory-safety check. Code generation, authentication policy and hardware support determine which pointers are protected.

The permitted-target set depends on the CFI policy. Type-based schemes may still permit an unintended same-type target; landing-pad schemes can permit a broader set. Shadow stacks protect returns by a different check, so a same-type target is not itself a shadow-stack bypass.

## Memory tagging

**Arm MTE** associates four-bit allocation tags with 16-byte granules of suitably configured memory and compares them with pointer tags on checked accesses. Software must arrange tagging and retagging; hardware does not infer every object lifetime. Four bits give 16 possible tags. Suppose a freed granule is retagged by an explicitly uniform, independent choice among all 16, and a stale pointer keeps its old tag:

```formula
T = 2^4 = 16
P_match = 1 / T
P_match = 1 / 16 = 0.0625 = 6.25%
where
T: the number of distinct tag values
2^4: 2 multiplied by itself 4 times, because each tag is 4 bits
P_match: the probability that the new tag happens to equal the stale pointer's tag, so the bad access is not caught
%: per cent, parts per hundred
In words: with 16 equally likely tags, a stale pointer's tag still matches about one time in 16, roughly 6%.
```

That probability describes one comparison in this simple model, not a real exploit success rate. Actual allocator policies, unchecked accesses and same-granule overflows change what is caught. In synchronous mode a mismatch is reported at the access; asynchronous mode can allow execution to continue before reporting.

Allocator hardening also narrows some failure modes. glibc safe-linking encodes selected singly linked free-list pointers; it does not prevent all heap corruption. Chrome BackupRefPtr, one MiraclePtr implementation, quarantines eligible allocations while tracked `raw_ptr` references remain. Untracked raw aliases and unsupported allocations are outside that guarantee.

## Summary table

| Mitigation | Breaks | Typical bypass |
|---|---|---|
| Canary | Return overwrite | Leak, non-linear write |
| DEP/NX | Injected code | Code reuse |
| ASLR | Known addresses | Info leak |
| Full RELRO | GOT overwrite | Other pointers |
| Type-based forward CFI | Invalid indirect-call targets | Unintended allowed target |
| Shadow stack | Faked returns | Unprotected code or disabled enforcement |
| MTE | Some invalid tagged accesses | Tag match or unchecked boundary |

> [!note] Defence in depth
> Combine protections and fix the source bug. Data-only corruption, information disclosure and failures outside what the enabled protections cover remain possible. Extra vulnerabilities are sometimes needed for exploitation, but a mitigation does not force every attacker to find another bug.

> [!note] Content omitted after review
> Universal ASLR defaults, platform-wide deployment rates, fixed exploit costs and guaranteed crash or prevention rates are omitted because this review did not establish the necessary versioned measurements. MTE and CET hardware enforcement were not exercised in this review.

## Key takeaways
- Mitigations restrict specific exploitation paths; they do not fix bugs or guarantee a safe outcome.
- Enabled canary checks detect some return-address overwrites; NX blocks execution from non-executable pages; ASLR varies selected mapping bases.
- Existing executable code can evade NX; a known-offset pointer leak can weaken ASLR for that mapping.
- CFI and shadow stacks constrain where indirect calls and returns can go; MTE catches many bad accesses directly.
- Use hardening supported by the target platform and verify both binary properties and runtime enablement.

## Further reading
- [Stack protection and instrumentation — GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
- [Linux virtual-memory sysctls](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [Control-flow integrity — Clang documentation](https://clang.llvm.org/docs/ControlFlowIntegrity.html)
- [CET shadow-stack requirements — Linux](https://docs.kernel.org/arch/x86/shstk.html)
- [DEP — Microsoft](https://learn.microsoft.com/en-us/windows/win32/memory/data-execution-prevention)
- [Source fortification — glibc](https://sourceware.org/glibc/manual/latest/html_node/Source-Fortification.html)
- [Compiler Options Hardening Guide for C and C++ — OpenSSF](https://best.openssf.org/Compiler-Hardening-Guides/Compiler-Options-Hardening-Guide-for-C-and-C++.html)
- [Memory Tagging Extension — Android](https://source.android.com/docs/security/test/memory-safety/arm-mte)
