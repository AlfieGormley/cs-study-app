---
id: isa-loops-arrays-structs
title: Loops, jump tables, arrays and structs in assembly
level: intermediate
minutes: 15
summary: How compilers lower if/else, loops and switch statements to branches and jump tables, and how array indexing and struct field access become address arithmetic.
---

The CPU has no idea what a `for` loop, a `switch` or a `struct` is. It has compares, conditional branches, and loads and stores with an address. Everything structured in your source code is *lowered* to those.

Once you know the handful of patterns compilers use, optimised assembly stops looking like noise. You can spot the loop in a profile, see why a `switch` became an indirect jump, and work out from `[rdi + rax*8 + 4]` which field of which array element is being read.

The listings are illustrative scalar implementations using Linux LP64 type sizes and System V x86-64 or AAPCS64 conventions. They are not promises of exact Clang output; version, flags and target change instruction selection. Assume valid object bounds and no signed C arithmetic overflow. Partial dispatch listings explicitly omit case bodies. Try them yourself on [Compiler Explorer](https://godbolt.org/).

## if/else: test, then branch around

One common lowering of an `if` uses a compare that sets flags and a conditional jump that **skips** the body. The jump condition is therefore usually the *inverse* of the source condition. Schematically:

```
// if (x > 0) y = 1; else y = 2;
    test  edi, edi
    jle   .Lelse       # skip if x <= 0
    mov   eax, 1
    jmp   .Ldone
.Lelse:
    mov   eax, 2
.Ldone:
```

When both arms are cheap and have no side effects, the compiler often removes the branch entirely with `cmov` (x86) or `csel` (ARM64). This can trade branch-misprediction costs for evaluating both candidate values; whether it helps depends on the core, dependencies and workload. A universal cycle penalty is omitted because no particular core or measurement is specified.

For this snippet another valid lowering is possible. It notices the result is `1 + (x <= 0)`:

```
    xor   eax, eax
    test  edi, edi
    setle al           # al = (x <= 0)
    inc   eax          # 1 or 2
```

No branch, no `cmov`: just flags turned into a number. This illustrates one possible rewrite; inspect actual compiler output to see whether it is used.

## Loops: the guarded do-while

Here is the canonical array sum:

```
long sum(long *a, long n) {
    long s = 0;
    for (long i = 0; i < n; i++)
        s += a[i];
    return s;
}
```

A naive translation tests `i < n` at the top and jumps back unconditionally at the bottom: two branches per iteration. Compilers can **rotate** the loop: check once on entry whether it runs at all, then put the test at the bottom.

```
sum:
    test  rsi, rsi
    jle   .Lzero          # n <= 0
    xor   ecx, ecx        # i = 0
    xor   eax, eax        # s = 0
.Lloop:
    add   rax, [rdi + 8*rcx]
    inc   rcx             # i++
    cmp   rsi, rcx
    jne   .Lloop          # until i == n
    ret
.Lzero:
    xor   eax, eax
    ret
```

Things to notice:

- The loop body is four instructions with **one** branch, taken every time except the last.
- `a[i]` is a single memory operand: base `rdi`, index `rcx`, scale 8 because a `long` is 8 bytes.
- The exit test became `i != n` rather than `i < n`. Once the guard has established `n > 0`, these are equivalent.

An A64 version turns the index into a moving pointer and a down-counter:

```
sum:
    cmp   x1, #1
    b.lt  .Lzero          // n < 1
    mov   x8, xzr         // s = 0
.Lloop:
    ldr   x9, [x0], #8    // load; +8 bytes
    subs  x1, x1, #1      // n--, set flags
    add   x8, x9, x8
    b.ne  .Lloop          // until n == 0
    mov   x0, x8
    ret
.Lzero:
    mov   x0, #0
    ret
```

The post-indexed load reads and advances the pointer in one instruction, and `subs` both decrements and sets the flags, so no separate compare is needed. Replacing `a + i*8` with a pointer bumped by 8 is classic **strength reduction**: an indexed-address recurrence becomes a pointer increment. The original scaled addressing did not necessarily require a separate multiply instruction.

> [!tip] Spotting loops in a listing
> Look for a **backward** branch: a conditional jump to a label *above* it. Then inspect the control-flow graph for a cycle; backward branches alone do not prove source-level loop boundaries in arbitrarily laid-out code. In `perf annotate` output, the hot instructions cluster inside it.

### What -O2 and -O3 add

At higher optimisation levels the same loop may grow considerably:

- **Unrolling**: the body is repeated (say four times per iteration) to cut loop overhead, with a cleanup loop for leftovers.
- **Vectorisation**: SIMD instructions (`paddq` on x86, `add v0.2d` on ARM64) add several elements at once. Remainders may use a scalar tail, masked vectors or other cleanup.
- **Loop-invariant code motion**: expressions proven invariant may move outside a loop when doing so preserves language semantics and is profitable.

So a five-line C loop can become fifty lines of assembly. A common structure is a guard, main loop and remainder handling; it is not universal.

## Arrays: address arithmetic

In byte-address notation, element `a[i]` starts at `base + i*s`, where `s` is the element size. C’s typed expression `a + i` already applies that scaling. x86-64 addressing modes can scale an index by 1, 2, 4 or 8, which covers `char`, `short`, `int`/`float` and `long`/`double`/pointers in a single operand. ARM64 does the same with a shifted register: `ldr w9, [x0, x1, lsl #2]` loads `a[i]` for a 4-byte `int`.

### 2-D arrays

C stores multidimensional arrays in **row-major** order: rows one after another. For `int a[R][C]`, with 4-byte `int`, element `a[i][j]` has byte address `base + (i*C + j)*4`; this is not a literal typed C pointer expression.

```
// int get(int a[][3], long i, long j)
get:
    lea   rax, [rsi + 2*rsi]   # i*3
    lea   rax, [rdi + 4*rax]   # &a[i]
    mov   eax, [rax + 4*rdx]   # a[i][j]
    ret
```

The compiler computes `i*3` with `lea` (no multiply), turns that into the address of row `i` (each row is 12 bytes, so `3i*4`), then indexes the column. Only the column count `C` matters; the number of rows never appears, which is why C lets you omit the first dimension in a parameter.

The order of your loops matters a lot for row-major data: walking `j` in the inner loop touches consecutive addresses, while walking `i` in the inner loop jumps 12 bytes (or 4 KB for a 1024-column `int` array) each step. That difference shows up in cache behaviour, covered in the memory-hierarchy module.

### Signed indices

If the index is a 32-bit `int` passed in from outside, it must be sign-extended before use as a 64-bit offset:

```
// long at(long *a, int i)
at:
    movsxd rax, esi       # sign-extend i
    mov   rax, [rdi + 8*rax]
    ret
```

Inside a loop where the compiler can prove `i` never goes negative, it usually promotes the counter to 64 bits once and drops the extension.

## Structs: fixed offsets

A struct is just a block of memory with each field at a **fixed offset** known at compile time. Each field has a type- and ABI-defined alignment, not necessarily equal to its size, and the struct's total size is rounded up to a multiple of its largest alignment so arrays of it stay aligned.

```
struct S {
    char  tag;   // offset 0
                 // 3 bytes padding
    int   n;     // offset 4
    long  v;     // offset 8
    short k;     // offset 16
                 // 6 bytes padding
};               // sizeof = 24
```

Fields add up to 1 + 4 + 8 + 2 = 15 bytes, yet the struct takes 24. Reordering from largest to smallest (`long`, `int`, `short`, `char`) needs 15 bytes plus 1 of tail padding: 16 bytes. Across a million-element array, the allocation saves 8,000,000 bytes. A full sequential byte scan has roughly one-third less data; actual cache-line traffic depends on alignment and which fields are accessed.

Field access is a constant displacement: `p->v` is `mov rax, [rdi + 8]`. Array-of-struct access combines both ideas:

```
// int getn(struct S *p, long i)
// returns p[i].n
getn:
    lea   rax, [rsi + 2*rsi]       # i*3
    mov   eax, [rdi + 8*rax + 4]   # p+24i+4
    ret
```

24 isn't a legal scale, so the compiler splits it as `3 × 8`: an `lea` for the 3 and the addressing mode's scale for the 8. The `+ 4` is the offset of `n`. Reading this backwards is a standard reverse-engineering skill: under the assumed direct p[i].field access, stride 24 and offset 4 reveal element size and field offset; they do not uniquely reconstruct the original type or declaration.

## switch: jump tables

A `switch` over **dense** case values can compile to a table of addresses and one indirect jump. Here five cases each call a different function:

```
// switch (x) { case 0: a(); ...
//              case 4: e(); }
sw:
    cmp   edi, 4
    ja    .Ldefault        # unsigned!
    mov   eax, edi
    lea   rcx, [rip + .Ltab]
    movsxd rax, [rcx + 4*rax]
    add   rax, rcx
    jmp   rax
.Ltab:
    .long .Lcase0 - .Ltab
    .long .Lcase1 - .Ltab
    ...
```

Step by step:

1. **One compare does the range check.** `ja` is an *unsigned* comparison, so a negative `x` such as -1 looks like 0xffffffff, which is "above" 4. Both `x < 0` and `x > 4` go to the default.
2. Load the table's address `rip`-relatively, so the code works wherever it is loaded.
3. The table holds 32-bit **offsets** relative to itself rather than absolute addresses. That halves its size and means no load-time patching is needed in position-independent executables.
4. Add the offset to the table base and jump.

For in-range inputs this sequence uses a fixed number of dispatch instructions, including one table load and one indirect branch. Elapsed time is not constant: caches and prediction matter, and out-of-range inputs take a different path. On ARM64 the same pattern uses `adr`, a load from the table and `br`.

### The compiler's other options

| Case values | Typical lowering |
|---|---|
| Few cases | chain of `cmp`/`je` |
| Dense range | jump table |
| Dense, each returns a constant | lookup table of values, no jump |
| Sparse (1, 1000, 50000) | binary search of compares |

The third row is worth knowing. `switch (x) { case 0: return 10; case 1: return 20; ... }` can become a range check and a table lookup; a simple arithmetic progression may instead become arithmetic. There's no branch at all apart from the range check.

## Trade-offs and pitfalls

- **Indirect branches are harder to predict.** A jump table with an unpredictable `x` mispredicts often. And after Spectre, indirect branches became a security concern: kernels built with retpoline mitigations have compiled with `-fno-jump-tables` so a `switch` becomes compares instead.
- **Reading `-O0` output.** Unoptimized code often spills and reloads locals, making a listing longer; no fixed size ratio applies. Read `-O1` or `-O2` to see what actually runs.
- **Aliasing blocks optimisation.** Possible aliasing can prevent some transformations, but compilers may use runtime overlap checks or other proofs. C `restrict` provides specific access-based promises that must be honored; it does not simply declare that every pointer has a different numerical address. Rust reference rules also have specific validity and aliasing constraints.
- **Padding surprises.** `sizeof` is often larger than the sum of the fields, which matters for file formats, network protocols and memory use. Use `offsetof` and static asserts instead of guessing.
- **Signed/unsigned mix-ups.** The unsigned range-check trick is safe in the compiler's hands, but in hand-written code a signed index compared with `ja`/`jb` can let a negative value through a bounds check, or the reverse.

## Key takeaways
- An `if` may use a compare and a branch on the inverted condition; cheap arms may become `cmov`/`csel`.
- Loops can be rotated into a guard plus a bottom-tested body; look for a backward branch to find them.
- `a[i]` is `base + i*size`; x86 scales by 1, 2, 4 or 8, ARM64 uses `lsl`; other sizes are built with `lea`.
- C arrays are row-major and struct fields sit at fixed, padded offsets; ordering suitable scalar fields by alignment often reduces padding, but is not a universal minimum-size rule for arbitrary types.
- Dense `switch` statements may become a range check (often a single unsigned compare) plus a jump table; sparse ones become compare trees.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [Branch table — Wikipedia](https://en.wikipedia.org/wiki/Branch_table)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Strength reduction — Wikipedia](https://en.wikipedia.org/wiki/Strength_reduction)
- [Loop unrolling — Wikipedia](https://en.wikipedia.org/wiki/Loop_unrolling)
- [Computer Systems: A Programmer's Perspective (CS:APP), chapter 3](https://csapp.cs.cmu.edu/)
