---
id: isa-guarded-sum-loops
title: Guarded loops, pointer walks and optimisation
level: intermediate
minutes: 4
sourceLesson: isa-loops-arrays-structs
summary: Trace scalar sums and recognise loop rotation and strength reduction.
---

These illustrative scalar listings use Linux LP64 type sizes: `long` is eight bytes. Arrays must be valid for every accessed element and signed C sums must remain representable. RDI/X0 hold the pointer; RSI/X1 hold the count.

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
    // Return the accumulated result.
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

## Key takeaways
- An entry guard preserves the zero-iteration case.
- A down-counter and post-indexed load can replace explicit indexing.
- Unrolling and vectorisation need remainder handling when applicable.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [Branch table — Wikipedia](https://en.wikipedia.org/wiki/Branch_table)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Strength reduction — Wikipedia](https://en.wikipedia.org/wiki/Strength_reduction)
- [Loop unrolling — Wikipedia](https://en.wikipedia.org/wiki/Loop_unrolling)
- [Computer Systems: A Programmer's Perspective (CS:APP), chapter 3](https://csapp.cs.cmu.edu/)
