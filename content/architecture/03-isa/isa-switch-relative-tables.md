---
id: isa-switch-relative-tables
title: Switch lowering and relative jump tables
level: intermediate
minutes: 5
sourceLesson: isa-loops-arrays-structs
summary: Trace switch dispatch, signed relative offsets and the compiler’s alternatives.
---

This schematic uses a signed 32-bit switch input in EDI under System V x86-64. Case bodies are omitted; table targets and table move together, and relative entries must fit signed 32 bits.

## switch: jump tables

A `switch` over **dense case values** can compile to a table of addresses and one indirect jump. Here five cases each call a different function:

```
// switch (x) { case 0: a(); ...
//              case 4: e(); }
sw:
    cmp   edi, 4
    ja    .Ldefault        # unsigned!
    # Only in-range cases reach the table.
    mov   eax, edi
    lea   rcx, [rip + .Ltab]
    # Entries are signed relative offsets.
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
- An unsigned range comparison can reject both negative and oversized cases.
- Relative entries retain their meaning when code and table move together.
- A compiler may instead use comparisons, values or arithmetic.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [Branch table — Wikipedia](https://en.wikipedia.org/wiki/Branch_table)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Strength reduction — Wikipedia](https://en.wikipedia.org/wiki/Strength_reduction)
- [Loop unrolling — Wikipedia](https://en.wikipedia.org/wiki/Loop_unrolling)
- [Computer Systems: A Programmer's Perspective (CS:APP), chapter 3](https://csapp.cs.cmu.edu/)
