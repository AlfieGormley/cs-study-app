---
id: par-vector-lanes
title: Vector widths, lanes and fused multiply-add
level: intermediate
minutes: 4
sourceLesson: par-simd
summary: Lane count follows register width and element width.
---

Adding two arrays of a million floats takes a million additions. A scalar instruction performs one such addition; a core may issue several instructions per cycle. But the adder hardware is cheap compared with the cost of fetching, decoding and scheduling an instruction. So CPU designers asked: why not make one instruction do *several* additions?

That is **SIMD** (single instruction, multiple data). Each register becomes a wide **vector register** holding several values side by side, called **SIMD lanes**, and one instruction operates on all lanes at once.

```
256-bit AVX register: 8 x float32
ymm1  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
ymm2  |10 |20 |30 |40 |50 |60 |70 |80 |
       ------ vaddps ymm0,ymm1,ymm2 ----
ymm0  |11 |22 |33 |44 |55 |66 |77 |88 |
```

One instruction, eight results. The possible speedup depends on instruction throughput, dependencies and memory traffic; lane count alone is not a measured speedup.

## The instruction set families

| ISA | Example vector width | Notes |
|---|---|---|
| SSE / SSE2 | 128 bits | x86 packed operations |
| AVX / AVX2 | 256 bits | AVX2 adds many 256-bit integer operations |
| AVX-512 | Up to 512 bits | Feature subsets differ; also supports masking |
| NEON / Advanced SIMD | 128 bits | Arm implementations that support this extension |
| SVE / SVE2 | 128–2048 bits | Current non-streaming SVE lengths are powers of two from 128 to 2048 bits; effective length is execution-context state. Earlier specifications differed. Target support required |

How many lanes you get depends on how wide the register is and how wide each element is:

```formula
L = W_reg / W_elem
L = 256 bits / 32 bits = 8
where
L: the number of lanes: how many elements one vector register holds side by side
W_reg: the width of the vector register, in bits; 128, 256 or 512 on x86
W_elem: the width of one element, in bits: 32 for float32, 64 for float64, 8 for int8
bits: binary digits, the unit of register and element width
In words: a register holds as many elements as fit in its width, so a 256-bit AVX register holds eight 32-bit floats.
```

The full table:

| Width | float32 | float64 | int8 |
|---|---|---|---|
| 128 | 4 | 2 | 16 |
| 256 | 8 | 4 | 32 |
| 512 | 16 | 8 | 64 |

**FMA** (fused multiply-add) is one instruction that multiplies two numbers and adds a third, rounding only once at the end:

```formula
d = ab + c
where
d: the result written to each lane
a: the first number being multiplied
b: the second number being multiplied
c: the number added to the product
In words: multiply two values and add a third in one step, with a single rounding instead of one after the multiply and another after the add.
```

Counting the multiply and the add as two FLOPs (floating-point operations) can double the arithmetic rate *if* FMA has the same lane count and sustained issue rate as the compared add-only instructions.

Some other notable details:
- **AVX-512** provides eight mask registers (`k0`–`k7`); ordinary EVEX writemasking uses `k1`–`k7`, with a zero mask-field encoding meaning no writemask. Masked operations can help with loop tails and conditionals.
- **SVE** permits vector-length-agnostic programs: correctly written code can adapt to different supported vector lengths without recompilation. Merely using SVE does not make every algorithm independent of vector length.

## Key takeaways
- Lane count follows register width and element width.
- FMA counts two arithmetic operations but rounds the combined operation once.

## Further reading
- [LLVM vectoriser mechanisms and legality](https://llvm.org/docs/Vectorizers.html)
- [GCC optimisation contracts](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Intel basic architecture and vector instructions](https://cdrdv2.intel.com/v1/dl/getContent/671436)
- [Arm SVE execution-context lengths](https://learn.arm.com/insights/sve/)
- [NumPy CPU dispatch](https://numpy.org/doc/stable/reference/simd/how-it-works.html)
