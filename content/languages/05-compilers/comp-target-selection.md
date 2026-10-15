---
id: comp-target-selection
title: "Instruction selection, ABIs and division semantics"
level: advanced
minutes: 5
sourceLesson: comp-codegen-regalloc
summary: "Instruction selection uses target patterns and costs while allocation respects ABI registers."
---

## Instruction selection

So far each IR operation became one instruction. Real instruction sets offer better choices. Here is representative optimised assembly for the C version of our example, for x86-64 (Intel syntax):

```c
int f(int x, int y) {
    // Keep inputs in the defined signed
    // range.
    return (x + y) * (x + y) - x * 8;
}
```

```
lea   eax, [rsi + rdi]
imul  eax, eax
shl   edi, 3
sub   eax, edi
ret
```

And for ARM64 (Apple silicon):

```
add  w8, w1, w0
mul  w8, w8, w8
sub  w0, w8, w0, lsl #3
ret
```

Several decisions are visible:

- **Common subexpressions.** `x + y` is computed once, as in our CSE.
- **`lea` as an adder.** x86's address-calculation instruction computes `rsi + rdi` into a fresh register without overwriting either input, unlike the traditional two-operand x86 add encoding.
- **Strength reduction.** `x * 8` becomes a shift: `shl edi, 3` on x86, and on ARM64 the shift is folded *into* the subtraction (`w0, lsl #3`), removing the separate multiply instruction; this does not imply zero execution cost.
- **Calling convention.** On x86-64 Linux (System V ABI), the first six eligible scalar integer arguments arrive in `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` and the result returns in `rax`. Under the usual AArch64 procedure-call standard, the first eight eligible integer arguments arrive in `x0` to `x7` (`w0`, `w1` are their 32-bit halves) and the result goes in `x0`. The register allocator works around these fixed registers.

The shift amount in the strength reduction comes from writing 8 as a power of two:

```formula
x × 8 = x × 2^3 = x << 3
where
x: the first integer argument, arriving in `edi`; the arithmetic identity applies to mathematical integers, while the shown machine instructions operate on their fixed-width bit patterns
2^3: 2 × 2 × 2, which is 8
<<: left shift: move every bit 3 places towards the more significant end, filling the gap with zeros
In words: multiplying by 8 is the same as shifting left by 3 places, which is what `shl edi, 3` does.
```

Selecting instructions is often framed as **tree tiling**: each machine instruction is a "tile" that covers a pattern of IR nodes (`lea` can cover a base register plus an index scaled by eight and a constant displacement), and the selector covers the tree with the cheapest set of tiles. LLVM's SelectionDAG and GlobalISel, and GCC's machine descriptions, are pattern-matching engines for exactly this. At -O0, compilers still allocate registers, but commonly retain stack locations and extra loads for debugging. Exact assembly depends on compiler, target and options. The C example assumes inputs whose signed arithmetic is defined.

> [!example] Floor versus truncation
> C's `x / 2` on signed `int` rounds towards zero, so Clang emits a shift *plus* a correction for negative numbers (`shr`, `add`, `sar` on x86). Calc's `/` is floor division, which is exactly what an arithmetic right shift computes, so a Calc value known to fit the signed machine word could use sar. Arbitrarily large Calc integers require more machinery. Language semantics shape the machine code.

The difference shows up only for negative odd numbers:

```formula
⌊−7 / 2⌋ = ⌊−3.5⌋ = −4
trunc(−7 / 2) = trunc(−3.5) = −3
−7 >> 1 = −4
where
⌊ ⌋: floor: round down, towards negative infinity; this is Calc's / and Python's //
trunc: truncation: drop the fractional part, rounding towards zero; this is C's / on integers
>>: arithmetic right shift: move every bit one place towards the less significant end, copying the sign bit into the gap; x86's `sar`
In words: shifting right by one place halves and rounds down, which matches floor division but is one too low for C's truncating division of a negative odd number.
```

Calling conventions also split registers into **caller-saved** (the callee may overwrite them, so the caller must save any live values before a call) and **callee-saved** (a function that uses them must preserve them: examples include `rbx`, `rbp` and `r12` to `r15` on x86-64 System V, alongside the stack pointer). A register allocator may choose callee-saved registers for values live across calls, balancing their save/restore cost against other options.

## Pitfalls

- **Register pressure from optimisation.** CSE and loop-invariant code motion keep values alive longer; too much of it causes spills that cost more than the recomputation saved.
- **Ignoring the ABI.** A value that must survive a call cannot sit in a caller-saved register unless it is saved around the call.
- **Benchmarking unoptimised builds.** -O0 prioritizes compilation and debugging over optimization; measure the build configuration relevant to your goal when comparing algorithms.
- **Assuming fewer instructions means faster.** Latency and throughput depend on the exact instruction and microarchitecture. Instruction selection uses target costs, not instruction count alone.

## Key takeaways
- Instruction selection uses target patterns and costs while allocation respects ABI registers.
- Arithmetic right shift rounds negative odd values down; C integer division truncates towards zero.

## Further reading
- [LLVM code generator design](https://llvm.org/docs/CodeGenerator.html)
- [Linear scan register allocation — Poletto and Sarkar](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Register allocation and coalescing research](https://www.cs.princeton.edu/~appel/modern/text/color1.html)
- [C11 committee draft: expressions and integer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [AArch64 procedure-call standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
