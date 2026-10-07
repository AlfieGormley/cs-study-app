---
id: sys-mitigations
title: Exploit mitigations
level: intermediate
minutes: 13
summary: Stack canaries, DEP/NX, ASLR, RELRO, FORTIFY_SOURCE, control-flow integrity, shadow stacks and memory tagging, what each one stops and what it doesn't.
---

Memory-unsafe operations can leave exploitable bugs in a program. Compilers, operating systems and CPUs provide **mitigations** that restrict particular ways of exploiting them. Their effectiveness depends on the enabled features and the program.

A mitigation does not repair the faulty source operation. It may prevent exploitation or terminate the process, but a crash is still an availability/security failure. A program may also leak information or corrupt sensitive data before a check fires. Some attacks need several vulnerabilities; there is no universal minimum chain length.

## The attacker's checklist

A classic control-flow attack may corrupt a return address or function pointer, determine a useful destination and redirect execution there. Other attacks change data, such as an authorization flag, without these steps.

The mitigations below address different parts of that process. None covers every possible memory-safety failure.

## Stack canaries

A **stack canary** is a guard value checked by compiler-generated code on protected function exits. A common downward-growing stack layout places it between buffers and the saved return address, as illustrated below; exact layout and coverage depend on the ABI, compiler and optimisation.

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

What canaries don't stop: heap overflows, overwrites of other data *before* the function returns (such as a function pointer used inside it), overflows within a struct (field order is fixed by the language), and attacks where a separate bug leaks the canary's value first.

## DEP / NX: data is not code

**DEP/NX** prevents instruction execution from pages marked non-executable. Write and execute permissions are separate: NX alone does not enforce **W^X**, the stronger policy that a page must not be writable and executable simultaneously. The table illustrates common permissions, not a guarantee for every mapping.

| Region | Read | Write | Execute |
|---|---|---|---|
| Code (.text) | yes | no | yes |
| Stack | yes | yes | no |
| Heap | yes | yes | no |

An attempt to fetch instructions from a non-executable stack or heap page faults. Whether the process then terminates depends on OS handling. A process can have executable mappings, including generated code; enabling DEP does not mean every data allocation is necessarily non-executable.

Attackers responded with **code-reuse** attacks: rather than injecting new code, they redirect control through short snippets of code that already exist in the program and its libraries, which are legitimately executable. The best-known form is **return-oriented programming** (ROP). Code reuse is why DEP alone is not enough, and why the attacker's "know where" step became so important.

JIT compilers generate executable code at run time. Their permission transitions and aliases need careful protection; a writable alias of executable storage can undermine the intended restriction. The exact mechanism is platform-specific.

## ASLR: hide the addresses

**Address space layout randomisation** varies placement of selected mappings, such as libraries and stacks, when a process image is loaded. Support and configuration determine which mappings vary. A fork normally inherits the existing address space. Wrong target guesses can fail or crash; neither outcome is guaranteed for every corruption.

How much it helps depends on **entropy**, the number of random bits:

- With eight independent uniformly random bits, there are `2^8 = 256` possibilities.
- With 28 such bits, there are `2^28 = 268,435,456` possibilities.

These are teaching examples, not asserted Linux defaults. Architecture, kernel settings and distribution policy affect actual entropy. On supported Linux systems, `vm.mmap_rnd_bits` controls randomisation for relevant mappings.

Two caveats make ASLR weaker than the numbers suggest:

1. **Leaks can weaken ASLR.** A pointer into a known library build at a known offset reveals that mapping base. It does not automatically reveal unrelated mappings or unknown builds.
2. **Coverage matters.** Conventional non-PIE ELF executables have fixed main-code addresses. PIE permits random placement when the loader and OS enable it; compiler flags alone are not proof of effective randomisation.

Linux can randomise its kernel base when **KASLR** is supported and enabled. A known-offset kernel pointer leak can weaken that protection.

## RELRO and FORTIFY_SOURCE

Two more toolchain hardening features are common on Linux:

- **RELRO** makes a designated ELF relocation region read-only after relocation. In a conventional supported ELF toolchain, full RELRO (`-Wl,-z,relro,-z,now`) also resolves lazy function bindings at load time so the GOT can be protected. Later `dlopen` loads have their own relocations. This does not protect every function pointer in a program.
- **`_FORTIFY_SOURCE`** adds compile-time diagnostics and run-time checks to supported library calls where object-size information is available. Level 3 uses dynamic object-size information and requires a compatible compiler/libc; glibc enables these wrappers only with optimisation. Unknown sizes and unsupported operations can remain unchecked.

An illustrative GNU/Linux ELF build fragment follows. It requires toolchain support for level-3 fortification; the CET-related flag is for supported x86 targets. Check platform documentation and the resulting binary/runtime configuration. Accepting a flag does not prove that hardware enforcement is active.

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

- **Clang CFI** includes type-based indirect-call and virtual-call checks. Its `-fsanitize=cfi` family requires the documented LTO/visibility setup; a flag alone is not a complete build recipe.
- **Microsoft CFG** validates instrumented indirect calls against allowed targets; it is not a complete type-based policy.
- **Intel IBT** and **Arm BTI** constrain relevant indirect branches to suitable landing pads when enforcement is enabled. Landing-pad validation is coarser than checking the intended function type.

### Backward edges: returns

A **shadow stack** keeps protected return-address copies. With x86 CET shadow-stack enforcement, calls update the two stacks and returns check agreement. Linux user-space use requires supporting CPU, kernel, runtime and enablement; kernel availability alone does not protect every application.

**Pointer authentication** can protect selected Arm pointers with a keyed authentication code, incorporating contextual information. It authenticates rather than encrypts the pointer, and is not a general memory-safety check. Code generation, authentication policy and hardware support determine coverage.

The permitted-target set depends on the CFI policy. Type-based schemes may still permit an unintended same-type target; landing-pad schemes can permit a broader set. Shadow stacks protect returns by a different check, so a same-type target is not itself a shadow-stack bypass.

## Memory tagging

**Arm MTE** associates four-bit allocation tags with 16-byte granules of suitably configured memory and compares them with pointer tags on checked accesses. Software must arrange tagging and retagging; hardware does not infer every object lifetime. Under an explicitly uniform independent choice among all 16 tags, a stale tag matches with probability `1/16`. Actual allocator policies, unchecked accesses and same-granule overflows change coverage. In synchronous mode a mismatch is reported at the access; asynchronous mode can allow execution to continue before reporting.

Allocator hardening also narrows some failure modes. glibc safe-linking encodes selected singly linked free-list pointers; it does not prevent all heap corruption. Chrome BackupRefPtr, one MiraclePtr implementation, quarantines eligible allocations while tracked `raw_ptr` references remain. Untracked raw aliases and unsupported allocations are outside that guarantee.

## Summary table

| Mitigation | Breaks | Typical bypass |
|---|---|---|
| Canary | Return overwrite | Leak, non-linear write |
| DEP/NX | Injected code | Code reuse |
| ASLR | Known addresses | Info leak |
| Full RELRO | GOT overwrite | Other pointers |
| Type-based forward CFI | Invalid indirect-call targets | Unintended allowed target |
| Shadow stack | Forged returns | Outside coverage or disabled enforcement |
| MTE | Some invalid tagged accesses | Tag match or unchecked boundary |

> [!note] Defence in depth
> Combine protections and fix the source bug. Data-only corruption, information disclosure and failures outside enabled coverage remain possible. Extra vulnerabilities are sometimes needed for exploitation, but a mitigation does not force every attacker to find another bug.

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
