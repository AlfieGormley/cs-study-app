---
id: isa-loops-arrays-structs
title: Loops, jump tables, arrays and structs in assembly
level: intermediate
minutes: 15
summary: How compilers lower if/else, loops and switch statements to branches and jump tables, and how array indexing and struct field access become address arithmetic.
---

The CPU has no idea what a `for` loop, a `switch` or a `struct` is. It has compares, conditional branches, and loads and stores with an address. Everything structured in your source code is *lowered* to those; this translation step is called **compiler lowering**.

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

For this snippet another valid lowering is possible. It notices the result is 1 plus a 0-or-1 flag:

```formula
y = 1 + c
c = 1 if x ≤ 0, otherwise 0
where
y: the result the if/else produces, 1 or 2
x: the input, held in edi
c: the condition turned into a number; `setle` (set if less than or equal) writes it
≤: less than or equal to
In words: a positive x gives 1 + 0 = 1, and anything else gives 1 + 1 = 2, exactly what the if/else computes.
```

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

A naive translation tests `i < n` at the top and jumps back unconditionally at the bottom: two branches per iteration. Compilers can **rotate the loop**: check once on entry whether it runs at all, then put the test at the bottom.

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

The post-indexed load reads and advances the pointer in one instruction, and `subs` both decrements and sets the flags, so no separate compare is needed. Replacing the multiply-based address with a pointer bumped by 8 is classic **strength reduction**: an indexed-address recurrence becomes a pointer increment.

```formula
p_i = a + i × 8
p_{i+1} = p_i + 8
where
p_i: the address of element i
p_{i+1}: the address of the next element
a: the address where the array starts
i: the element index, counting from 0
8: the size of a `long` in bytes
In words: instead of multiplying the index by 8 every time, keep the previous address and add 8; with a = 0x1000, the addresses run 0x1000, 0x1008, 0x1010 and so on.
```

The original scaled addressing did not necessarily require a separate multiply instruction.

> [!tip] Spotting loops in a listing
> Look for a **backward** branch: a conditional jump to a label *above* it. Then inspect the control-flow graph for a cycle; backward branches alone do not prove source-level loop boundaries in arbitrarily laid-out code. In `perf annotate` output, the hot instructions cluster inside it.

### What -O2 and -O3 add

At higher optimisation levels the same loop may grow considerably:

- **Unrolling**: the body is repeated (say four times per iteration) to cut loop overhead, with a cleanup loop for leftovers.
- **Vectorisation**: SIMD instructions (`paddq` on x86, `add v0.2d` on ARM64) add several elements at once. Leftover elements may use a scalar tail, masked vectors or other cleanup.
- **Loop-invariant code motion**: expressions proven invariant may move outside a loop when doing so preserves language semantics and is profitable.

So a five-line C loop can become fifty lines of assembly. A common structure is a guard, main loop and remainder handling; it is not universal.

## Arrays: address arithmetic

Element `a[i]` starts at a fixed distance from the start of the array:

```formula
addr = base + i × s
addr = 0x1000 + 5 × 4 = 0x1014
where
addr: the byte address where element i starts
base: the address of element 0, the start of the array (here 0x1000, hexadecimal)
i: the element index, counting from 0 (here 5)
s: the element size in bytes (here 4, for an `int`)
In words: skip i whole elements of s bytes each; element 5 of an int array at 0x1000 starts 20 bytes in, at 0x1014.
```

C’s typed expression `a + i` already applies that scaling. x86-64 addressing modes can scale an index by 1, 2, 4 or 8, which covers `char`, `short`, `int`/`float` and `long`/`double`/pointers in a single operand. ARM64 does the same with a shifted register: `ldr w9, [x0, x1, lsl #2]` loads `a[i]` for a 4-byte `int`.

### 2-D arrays

C stores multidimensional arrays in **row-major** order: rows one after another. For `int a[R][C]` (R rows of C columns), with 4-byte `int`, element `a[i][j]` sits after i complete rows and j more elements:

```formula
addr = base + (i × C + j) × 4
addr = base + (2 × 3 + 1) × 4 = base + 28
where
addr: the byte address of element a[i][j]
base: the address of a[0][0], where the array starts
i: the row index, counting from 0 (here 2)
j: the column index, counting from 0 (here 1)
C: the number of columns per row (here 3)
4: the size of an `int` in bytes
In words: count how many elements come before a[i][j] in the long row-by-row line (2 rows of 3, plus 1, makes 7), then turn that count into bytes.
```

This is byte arithmetic, not a literal typed C pointer expression. The listing below has C = 3.

```
// int get(int a[][3], long i, long j)
get:
    lea   rax, [rsi + 2*rsi]   # i*3
    lea   rax, [rdi + 4*rax]   # &a[i]
    mov   eax, [rax + 4*rdx]   # a[i][j]
    ret
```

The compiler computes `i*3` with `lea` (no multiply), turns that into the address of row `i` (each row is 3 × 4 = 12 bytes, so row i starts 12 × i bytes in), then indexes the column. Only the column count `C` matters; the number of rows never appears, which is why C lets you omit the first dimension in a parameter.

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

Fields add up to 1 + 4 + 8 + 2 = 15 bytes, yet the struct takes 24. Reordering from largest to smallest (`long`, `int`, `short`, `char`) leaves no gaps between fields, so only the end needs rounding up:

```formula
s_S = ⌈s_f / A⌉ × A
s_S = ⌈15 / 8⌉ × 8 = 2 × 8 = 16
Δ = (24 − 16) × 1000000 = 8000000
where
s_S: the size of the struct in bytes (what `sizeof` reports)
s_f: the bytes used by the fields plus any padding between them: 15, with no gaps in this order
A: the struct's alignment: the largest alignment of any field, 8 for the `long`
⌈ ⌉: ceiling: round up to the next whole number
Δ: the bytes saved across an array of a million structs
In words: round the fields' total up to the next multiple of the largest alignment, so 15 bytes become 16, and a million structs shrink by 8,000,000 bytes.
```

The rounding only accounts for tail padding; in the original order, the 3 bytes after `tag` are padding between fields, which is why that layout needs 24. A full front-to-back byte scan has roughly one-third less data; actual cache-line traffic depends on alignment and which fields are accessed.

Field access is a constant displacement: `p->v` is `mov rax, [rdi + 8]`. Array-of-struct access combines both ideas:

```
// int getn(struct S *p, long i)
// returns p[i].n
getn:
    lea   rax, [rsi + 2*rsi]       # i*3
    mov   eax, [rdi + 8*rax + 4]   # p+24i+4
    ret
```

```formula
addr = p + 24 × i + 4
addr = p + 8 × (3 × i) + 4
addr = p + 24 × 2 + 4 = p + 52
where
addr: the address of p[i].n
p: the address of the first struct in the array
i: which struct, counting from 0 (here 2)
24: sizeof(struct S): the stride from one struct to the next
4: the offset of field n inside each struct
In words: jump over i whole 24-byte structs, then 4 bytes into the one you want.
```

24 isn't a legal scale, so the compiler splits it as `3 × 8`: an `lea` for the 3 and the addressing mode's scale for the 8. The `+ 4` is the offset of `n`. Reading this backwards is a standard reverse-engineering skill: under the assumed direct p[i].field access, stride 24 and offset 4 reveal element size and field offset; they do not uniquely reconstruct the original type or declaration.

## switch: jump tables

A `switch` over **dense case values** can compile to a table of addresses and one indirect jump. Here five cases each call a different function:

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

1. **One compare does the range check.** `ja` is an *unsigned* comparison, so a negative `x` looks like a huge number:

```formula
u = x          for x ≥ 0
u = x + 2^32   for x < 0
u = −1 + 4294967296 = 4294967295
where
u: how the unsigned comparison sees the 32 bits of x
x: the switch value as a signed 32-bit int
2^32: 4,294,967,296, the number of different 32-bit patterns
≥, <: greater than or equal to, less than
In words: −1 is read as 4,294,967,295 (0xffffffff), which is "above" 4, so every negative x and every x above 4 goes to the default with a single test.
```

2. Load the table's address `rip`-relatively, so the code works wherever it is loaded.
3. The table holds 32-bit **offsets** relative to itself rather than absolute addresses. That halves its size and means no load-time patching is needed in position-independent executables.
4. Add the offset to the table base and jump:

```formula
E_x = T + 4 × x
target = T + d_x
where
E_x: the address of table entry number x
T: the address of the table, .Ltab
x: the switch value, 0 to 4 after the range check
4: each entry is a 4-byte (32-bit) offset
target: the address of the case code that `jmp rax` goes to
d_x: the signed offset stored in entry x (`.Lcase0 - .Ltab` and so on)
In words: read the 4-byte entry for case x, then add that offset to the table's own address to find where to jump.
```

For in-range inputs this sequence uses a fixed number of dispatch instructions, including one table load and one indirect branch. Elapsed time is not constant: caches and prediction matter, and out-of-range inputs take a different path. On ARM64 the same pattern uses `adr`, a load from the table and `br`.

### The compiler's other options

| Case values | Typical lowering |
|---|---|
| Few cases | chain of `cmp`/`je` |
| Dense range | jump table |
| Dense, each returns a constant | lookup table of values, no jump |
| Sparse (1, 1000, 50000) | binary search of compares |

The third row is worth knowing. `switch (x) { case 0: return 10; case 1: return 20; ... }` can become a range check and a lookup in a table of values; a simple arithmetic progression may instead become arithmetic. There's no branch at all apart from the range check.

## Trade-offs and pitfalls

- **Indirect branches are harder to predict.** A jump table with an unpredictable `x` mispredicts often. And after Spectre, indirect branches became a security concern: kernels built with retpoline mitigations have compiled with `-fno-jump-tables` so a `switch` becomes compares instead.
- **Reading `-O0` output.** Unoptimized code often spills and reloads locals, making a listing longer; no fixed size ratio applies. Read `-O1` or `-O2` to see what actually runs.
- **Aliasing blocks optimisation.** Possible aliasing can prevent some transformations, but compilers may use runtime overlap checks or other proofs. C's `restrict` keyword provides specific access-based promises that must be honored; it does not simply declare that every pointer has a different numerical address. Rust reference rules also have specific validity and aliasing constraints.
- **Padding surprises.** `sizeof` is often larger than the sum of the fields, which matters for file formats, network protocols and memory use. Use `offsetof` and static asserts instead of guessing.
- **Signed/unsigned mix-ups.** The unsigned range-check trick is safe in the compiler's hands, but in hand-written code a signed index compared with `ja`/`jb` can let a negative value through a bounds check, or the reverse.

## Key takeaways
- An `if` may use a compare and a branch on the inverted condition; cheap arms may become `cmov`/`csel`.
- Loops can be rotated into a guard plus a bottom-tested body; look for a backward branch to find them.
- `a[i]` sits at the array's base address plus the index times the element size; x86 scales by 1, 2, 4 or 8, ARM64 uses `lsl`; other sizes are built with `lea`.
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
