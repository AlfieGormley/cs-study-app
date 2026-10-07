---
id: isa-compile-link-load
title: Compile, assemble, link and load, plus NX, ASLR and canaries
level: advanced
minutes: 18
summary: How source code becomes a running process (object files, relocations, ELF, static and dynamic linking through the PLT and GOT, the loader) and how NX, ASLR and stack canaries harden the result.
---

Typing `gcc hello.c` feels like one step. It has preprocessing, compilation, assembly and linking stages (which need not be separate programs or materialized files), and then the kernel and a dynamic loader cooperate to turn the final file into a process.

Knowing this pipeline explains error messages you will meet ("undefined reference", "relocation truncated", "cannot find -lfoo"), why lazy binding can add work to a first library call, and where the operating system's memory-safety defences come from.

## The pipeline

```flow
hello.c: C source
cpp: preprocess #include and #define
hello.i: preprocessed source
cc1: compile to assembly
hello.s: assembly
as: assemble to machine code
hello.o: relocatable object
ld: link with libc and crt files
a.out: executable
execve + ld.so: load and run
Running process
```

`gcc -save-temps hello.c` keeps every intermediate file so you can look at each. `gcc -v` prints the exact commands the driver runs, including the start-up objects (`crt1.o`, `crti.o` and friends) it links in for you.

The interesting boundary is between the assembler and the linker. In ordinary separate compilation a compiler processes one translation unit at a time (link-time optimization can cross that boundary), so when `hello.c` calls `puts`, nobody yet knows where `puts` will live.

## Object files: code with holes

The assembler produces a **relocatable object file**. On Linux it is in **ELF** (Executable and Linkable Format), the same format used for executables, shared libraries and core dumps. An object file contains:

- **Sections**: `.text` (code), `.rodata` (constants and string literals), `.data` (initialised globals), `.bss` (zero-initialised globals, whose zero-filled payload occupies no file bytes; section metadata still exists).
- A **symbol table**: names this file defines (`main`) and names it uses but doesn't define (`puts`, marked undefined).
- **Relocations**: a list of locations in code or data that may require fixups once final addresses are known.

Disassembling `hello.o` with `objdump -dr` shows the hole:

```
e8 00 00 00 00   call  <main+0x9>
     R_X86_64_PLT32  puts-0x4
```

The `call` is encoded with a zero displacement, and the relocation entry says: "when you know where `puts` (or its PLT stub) is, put the PC-relative distance here, minus 4 because the displacement is measured from the end of the instruction".

## Static linking

A linker such as GNU `ld`, `gold`, LLVM `lld` or `mold` does two jobs.

**1. Symbol resolution.** Resolve symbol references according to binding and visibility rules. Undefined weak symbols and dynamic imports are exceptions to a simple one-definition model.

- No definition: `undefined reference to 'foo'`.
- Two strong definitions: `multiple definition of 'foo'`.
- With traditional GNU ld archive processing, static archives (`libfoo.a`) are searched **in command-line order**, and only members that satisfy a currently undefined symbol are pulled in. So `gcc -lm main.o` can fail where `gcc main.o -lm` works: when that archive was first considered, the required reference had not yet appeared. Archive groups can cause repeated searches; other linkers such as LLD have different backward-reference handling.

**2. Relocation.** Lay out all the sections in the output, assign each symbol a final address, then walk the relocation list and patch every hole.

A fully static executable contains copies of every library function it uses. This reduces dependencies on shared-library files for the linked code, but does not remove all runtime resources or guarantee faster startup or a larger final binary, and every program must be relinked to pick up a library security fix.

## Sections versus segments

An executable has two views of the same bytes. **Sections** are for the linker and tools. **Segments** (listed in the program headers) tell the loader what to map into memory, and with which permissions. `readelf -lW` on a typical PIE shows, simplified:

```
Type      Flags  Contents
PHDR      R      program headers
INTERP    R      /lib64/ld-linux-...
LOAD      R      headers, .dynsym...
LOAD      R E    .text .plt
LOAD      R      .rodata
LOAD      RW     .data .bss .got
DYNAMIC   RW     dynamic-link info
GNU_STACK RW     stack: not exec
GNU_RELRO varies  protect after relocation
```

This schematic has no RWX load segment; actual linker output and permission flags vary. GNU_STACK describes stack policy, and GNU_RELRO identifies a range to protect rather than adding another independent mapping. Note that no LOAD entry shown is both writable and executable. That is deliberate, and it matters for security below.

## Dynamic linking

Most programs link against **shared libraries** (`libc.so.6`) instead. The executable records only which libraries it needs (`DT_NEEDED` entries; inspect them with `readelf -d`). Processes mapping the same unchanged library file can share its code pages. Replacing a library file normally benefits newly started processes; existing processes can retain the old mapping until restarted. ABI compatibility, containers and bundled copies also matter.

The catch: the library's load address isn't known until run time, and differs between processes. Code must still be able to find functions and globals in other modules without the loader rewriting the code pages, which would stop them being shared.

### PIC and the GOT

Shared libraries commonly use **position-independent code** (PIC). Code refers to its own functions and data with `rip`-relative addressing (or `adrp` on ARM64), which works wherever the module is loaded.

For symbols requiring runtime address resolution, a common PIC mechanism uses a table of pointers in the module's writable data: the **Global Offset Table** (GOT). The loader resolves applicable GOT entries; some function slots can instead be bound lazily. The code reads the pointer from the GOT, again `rip`-relatively, and uses it:

```
mov  rax, [rip + environ@GOTPCREL]
mov  rax, [rax]     # value of environ
```

This mechanism relocates pointer slots rather than rewriting those instruction bytes; other writable data or relocation targets can still differ per process, while the code stays read-only and shared.

### The PLT and lazy binding

External calls can go through the **Procedure Linkage Table** (PLT), a set of small stubs in the executable's code. Classic x86-64 lazy binding works like this:

```
puts@plt:
    jmp   [rip + puts@GOT]
    push  0             # reloc index
    jmp   .plt0         # to resolver
```

1. `main` executes `call puts@plt`.
2. The stub jumps through puts's GOT slot. On the **first** call, that slot points back at the stub's own `push`.
3. The stub pushes the relocation index and jumps to `.plt0`, which calls the dynamic loader's resolver.
4. The resolver looks `puts` up in the loaded libraries, **writes its real address into the GOT slot**, and jumps to it.
5. Every **later** call goes stub → GOT → `puts` directly: one extra indirect jump.

Lazy binding can reduce startup resolution work for programs that link against thousands of functions but call few of them. The alternative, `-z now` (or `LD_BIND_NOW=1`), requests eager binding of the object’s required dynamic symbols at load time. Combined with **full RELRO** (`-z relro -z now`), the loader then makes the GOT read-only, so ordinary writes cannot overwrite the protected GOT slots. Other writable control data and permission-changing capabilities remain separate concerns. Many distributions build packages this way. `-fno-plt` goes further and calls through the GOT directly, skipping the stub.

## Loading: from execve to main

For a conventional dynamically linked glibc ELF program on Linux:

1. The kernel's `execve` reads the ELF header and program headers, and maps each `LOAD` segment with its permissions.
2. Because there is an `INTERP` segment, it also maps the dynamic loader (`/lib64/ld-linux-x86-64.so.2`).
3. It builds the initial stack: `argc`, `argv`, `envp`, and an **auxiliary vector** (page size, entry point address, a pointer to 16 random bytes, and so on). Then it jumps to the *loader's* entry point.
4. `ld.so` maps dependencies, performs required relocations (leaving lazy slots where applicable), and runs loader-managed initialization before transferring to the program's `_start`.
5. `_start` calls `__libc_start_main`, which handles remaining initialization, including the main executable’s initialization functions in the glibc 2.39 path reviewed here, then invokes main. The third envp parameter is a platform extension, not the ISO C two-argument main signature.

You can watch this with `LD_DEBUG=libs ./prog` or `strace ./prog`, which shows the `mmap` calls for each library before your code runs.

## Hardening: why the defences exist

An out-of-bounds access violates C/C++ rules and has undefined behaviour, but ordinary native code often lacks runtime bounds checks. On the stack, a buffer sits just below the saved registers and the **return address** (see the calling-conventions lesson). An out-of-bounds write that is long enough can overwrite that address, so when the function returns, control goes somewhere an attacker chose.

Fixing every such bug is the real cure, and memory-safe languages remove whole classes of them. In the meantime, three widely used mitigations make these bugs much harder to turn into control of the machine. Each is a layer, and each has known limits.

### NX: data is not code

Early exploits placed machine code in the overflowing buffer and returned into it. **NX** (no-execute; Intel calls it XD, Windows calls the policy DEP, ARM has XN, UXN and PXN) uses architectural execute permissions. In x86-64 paging with NX supported and EFER.NXE enabled, bit 63 of relevant paging-structure entries can prohibit execution. If effective permissions prohibit execution, an instruction fetch faults.

A **W^X** policy aims to avoid simultaneously writable and executable mappings; enforcement and exceptions depend on the OS and configuration. The stack, heap and `.data` are non-executable in typical hardened layouts (`GNU_STACK RW` specifically requests a non-executable stack, not heap/data policy); `.text` is read-only.

Limits: NX blocks instruction fetches from non-executable mappings; it does not prevent injected code running in an executable mapping, or attacks that reuse existing code, chaining together fragments already in `.text` and libc (return-oriented programming). It also complicates JIT compilers, which must write code and then execute it; follow platform JIT permission, cache-maintenance and synchronization rules. Separate RW/RX aliases satisfy only a mapping-level W^X rule, not a stronger prohibition on writable access to executable backing memory.

### ASLR: unpredictable addresses

Code-reuse attacks need to know *where* things are. **Address space layout randomisation** places the stack, heap, `mmap` regions, shared libraries and (for PIE binaries) the executable itself at randomized addresses when enabled, subject to platform constraints; repeated addresses remain possible.

- Linux controls it with `/proc/sys/kernel/randomize_va_space` (2 adds heap randomization to mode 1; defaults depend on kernel configuration and system policy).
- The executable is randomised only if it is built as a **PIE** (typically ELF Type DYN, but DYN also describes shared objects). Compiler defaults are toolchain-specific; use `-fPIE -pie` explicitly when appropriate, which is one reason the jump tables in the previous lesson use relative offsets.
- Address width permits more randomization space but does not determine effective entropy. A fixed default-bit count and universal attack-time estimate are omitted because architecture, kernel configuration and deployment determine them.

Limits: ASLR randomises a module's *base*, and everything inside keeps its relative position. With a matching binary and a correctly identified symbol, a leaked address can reveal that module’s base and the locations of objects at known offsets. Arbitrary leaked pointers, symbol interposition and indirect-function implementations need additional identification. A forked child inherits its parent's existing mapping addresses; subsequent mapping changes or exec can make their layouts diverge. KASLR can also randomize the kernel base when supported and enabled.

### Stack canaries: detect the overwrite

A **stack canary** (or stack protector) is a random value placed between a function's local buffers and its saved registers and return address. Before returning, the function checks it is unchanged. In a protected layout, a contiguous overwrite toward the return address crosses the guard. Detection requires that it actually change the guard and that execution reach a check.

Here is an illustrative x86-64 Linux/glibc stack-protector layout for a 32-byte local buffer. The ellipsis marks omitted application code; exact compiler output and layout vary:

```
greet:
    push  rbx
    sub   rsp, 48
    mov   rsi, rdi
    mov   rax, qword ptr fs:[40]
    mov   qword ptr [rsp + 40], rax
    ...                   # use buf
    mov   rax, qword ptr fs:[40]
    cmp   rax, qword ptr [rsp + 40]
    jne   .Lfail
    add   rsp, 48
    pop   rbx
    ret
.Lfail:
    call  __stack_chk_fail@PLT
```

```
rsp+56  return address
rsp+48  saved rbx
rsp+40  canary
rsp+32  (padding)
rsp+0   buf[32]
```

- In the glibc 2.39 x86-64 layout reviewed here, the stack guard is accessed in thread-local storage at `fs:0x28` (40). It is chosen at start-up from the kernel-supplied random bytes, with its lowest byte forced to zero to impede string-based disclosure and overwrite across the guard. A terminating zero can still overwrite its first byte unchanged; this is not protection against every overwrite or leak.
- `__stack_chk_fail` prints "stack smashing detected" and aborts. A crash is a far better outcome than a hijack.
- `-fstack-protector-strong` covers additional functions with local arrays or references to local frame addresses; optimized-away or register-only objects do not count. Defaults depend on compiler and build configuration. `-fstack-protector-all` instruments every function at a higher cost.

Limits: a canary detects a mismatch when its check executes. A non-contiguous write that hits the canary may also be detected; writes that bypass it or cause harm before the check can escape that protection. A bug that writes to an arbitrary address, overwrites a function pointer among the locals, or first leaks the canary can avoid it. Forked children inherit the parent's canary.

## Defence in depth

| Mitigation | Stops | Weakness |
|---|---|---|
| NX / W^X | execution from protected data mappings | executable mappings and code reuse |
| ASLR + PIE | hard-coded addresses | info leaks |
| Canaries | some overwrites crossing the guard | arbitrary writes |
| Full RELRO | GOT overwrites | other pointers |

Additional mechanisms can reduce particular attack paths when hardware, OS, compiler and application support enable them. Intel CET adds a **shadow stack** (a protected copy of return addresses checked on every `ret`) and indirect-branch tracking. ARM64 has **pointer authentication** (PAC, signing return addresses in spare pointer bits) and **branch target identification** (BTI). With a supporting libc and compiler configuration, `_FORTIFY_SOURCE` can add checks to selected library operations using inferred object sizes; it does not bounds-check every memory access.

To audit a binary, `checksec --file=prog` (from the checksec project) or `readelf -lW` and `readelf -d` show which of these are enabled. These are the first things a security review of a native binary checks.

## Pitfalls

- **Disabling mitigations "to make it work".** `-z execstack` or `-fno-stack-protector` in a build script usually hides a real bug.
- **Thinking ASLR makes leaks harmless.** Printing a pointer in an error message can defeat it for the whole module.
- **Library order** on the link line, and confusing `.a` with `.so` behaviour.
- **Assuming mitigations replace fixing bugs.** They raise the cost of exploitation; they don't remove the vulnerability.

## Key takeaways
- `gcc` runs the preprocessor, compiler, assembler and linker; object files are ELF with sections, symbols and relocations.
- The linker resolves symbols and patches relocations; traditional GNU ld archive extraction is order-sensitive, with grouping and linker-specific exceptions.
- Shared libraries use PIC: external data through the GOT, some external calls through PLT stubs, resolved lazily or at start-up (`-z now`, full RELRO).
- `execve` maps the segments and the dynamic loader, which loads libraries and relocates before `_start` calls `main`.
- NX/W^X, ASLR with PIE, and stack canaries each block one step of exploiting memory bugs, and each has known limits; use them together, and still fix the bugs.

## Further reading
- [Executable and Linkable Format — Wikipedia](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format)
- [elf(5) — Linux manual page](https://man7.org/linux/man-pages/man5/elf.5.html)
- [ld.so(8) — Linux manual page](https://man7.org/linux/man-pages/man8/ld.so.8.html)
- [Position Independent Code in shared libraries — Eli Bendersky](https://eli.thegreenplace.net/2011/11/03/position-independent-code-pic-in-shared-libraries/)
- [All about Procedure Linkage Table — MaskRay](https://maskray.me/blog/2021-09-19-all-about-procedure-linkage-table)
- [How To Write Shared Libraries — Ulrich Drepper (PDF)](https://www.akkadia.org/drepper/dsohowto.pdf)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [NX bit — Wikipedia](https://en.wikipedia.org/wiki/NX_bit)
- [Buffer overflow protection — Wikipedia](https://en.wikipedia.org/wiki/Buffer_overflow_protection)
- [GCC instrumentation options (-fstack-protector)](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)

### Primary implementation references
- [GNU ld options and archive/RELRO rules](https://sourceware.org/binutils/docs/ld/Options.html)
- [Linux ASLR control](https://docs.kernel.org/admin-guide/sysctl/kernel.html#randomize-va-space)
- [glibc 2.39 stack-guard setup](https://github.com/bminor/glibc/blob/glibc-2.39/sysdeps/unix/sysv/linux/dl-osinfo.h)
- [glibc 2.39 startup](https://github.com/bminor/glibc/blob/glibc-2.39/csu/libc-start.c)
