---
id: par-simd
title: SIMD and vectorisation
level: intermediate
minutes: 13
summary: How one instruction can process 4, 8 or 16 values at once with SSE, AVX and NEON, what stops compilers vectorising your loops, and how to write code they can.
---

Adding two arrays of a million floats takes a million additions. A scalar core does them one per instruction. But the adder hardware is cheap compared with the cost of fetching, decoding and scheduling an instruction. So CPU designers asked: why not make one instruction do *several* additions?

That is **SIMD** (single instruction, multiple data). Registers become wide **vectors** holding several values, called **lanes**, and one instruction operates on all lanes at once.

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
| SVE / SVE2 | 128–2048 bits | In 128-bit increments; target support required |

How many lanes you get depends on element size:

| Width | float32 | float64 | int8 |
|---|---|---|---|
| 128 | 4 | 2 | 16 |
| 256 | 8 | 4 | 32 |
| 512 | 16 | 8 | 64 |

Some notable details:

- **FMA** computes `a × b + c` with one rounding. Counting a multiply and add as two FLOPs can double the arithmetic rate *if* FMA has the same lane count and sustained issue rate as the compared add-only instructions.
- **AVX-512** provides eight mask registers (`k0`–`k7`); ordinary EVEX writemasking uses `k1`–`k7`, with a zero mask-field encoding meaning no writemask. Masked operations can help with loop tails and conditionals.
- **SVE** permits vector-length-agnostic programs: correctly written code can adapt to different supported vector lengths without recompilation. Merely using SVE does not make every algorithm independent of vector length.

### Peak throughput

A hypothetical core sustaining two 256-bit float32 FMAs per cycle delivers 2 × 8 × 2 = **32 FLOPs per cycle**. At a sustained 3 GHz that is 96 GFLOP/s. A hypothetical scalar baseline sustaining one add per cycle delivers 3 GFLOP/s; this compares different operations and assumes the stated throughput. Real peak and useful performance require target-specific instruction and memory measurements.

## Writing SIMD by hand: intrinsics

Compilers expose vector instructions as **intrinsics**, C functions that map almost one-to-one onto instructions. Here is an AVX array addition:

```c
#include <immintrin.h>
#include <stddef.h>

void add(float *a, const float *b,
         const float *c, size_t n) {
  size_t i = 0;
  for (; n - i >= 8; i += 8) {
    __m256 vb = _mm256_loadu_ps(b + i);
    __m256 vc = _mm256_loadu_ps(c + i);
    __m256 va = _mm256_add_ps(vb, vc);
    _mm256_storeu_ps(a + i, va);
  }
  for (; i < n; i++)   /* scalar tail */
    a[i] = b[i] + c[i];
}
```

Precondition: each pointer provides at least n valid floats; the output range does not overlap either input range. The two read-only input ranges may overlap. Compile for an AVX-capable execution environment. These explicit intrinsics do not insert a scalar fallback for unsafe overlap.

Note the two loops. The main loop handles eight elements per iteration; the **tail** loop handles the leftover n mod 8 elements. `loadu` means "unaligned load"; its performance depends on the target, alignment, cache-line and page boundaries.

The NEON version looks the same with different names: `float32x4_t`, `vld1q_f32`, `vaddq_f32`, `vst1q_f32`, four lanes at a time.

## Letting the compiler do it: auto-vectorisation

Intrinsics target particular extensions. Auto-vectorisation lets a compiler select transformations for its target and cost model. Current Clang enables loop vectorisation at `-O2`; GCC also enables it at `-O2`, with a more conservative cost model than `-O3`. Check the actual compiler version and optimisation report. On x86, `-mavx2` enables AVX2 instructions; `-march=native` targets the build machine and may produce binaries unsuitable for other machines.

Ask the compiler what it did: `-fopt-info-vec-missed` (GCC) or `-Rpass-missed=loop-vectorize` (Clang).

### What blocks vectorisation

**1. Possible aliasing.** In a scalar array-add loop, if `a` overlaps `b` shifted by one element, one iteration may feed the next. A compiler needs a safe transformation, potentially using a runtime overlap check. The manual kernel above instead requires disjoint output. C's `restrict` can express exclusive access to modified objects through the relevant pointer; two read-only inputs may still alias:

```c
void add(float *restrict a,
         const float *restrict b,
         const float *restrict c,
         size_t n);
```

**2. Loop-carried dependencies.** Here each iteration needs the previous result, so lanes cannot run independently:

```c
for (i = 1; i < n; i++)
  a[i] = a[i - 1] * 0.5f + b[i];
```

**3. Floating-point reductions.** Independent partial sums change the addition order. The error can be much larger than a last-bit difference, and overflow or special values can behave differently. Reassociation requires an appropriate numerical contract; GCC's `-fassociative-math` has additional prerequisites, and `-ffast-math` relaxes several rules, not just ordering. Some targets support ordered vector reductions without reassociation. Unsigned integer addition is associative modulo its width; signed overflow is undefined in C. Legal vectorisation still depends on the target and cost model.

**4. Branches.** SIMD lanes cannot take different paths. The compiler may **if-convert** safe work into per-lane selects or masked operations. It cannot blindly evaluate both sides if that introduces invalid accesses, exceptions or observable side effects.

```c
/* compare/select candidate */
for (i = 0; i < n; i++)
  a[i] = b[i] > 0 ? b[i] : 0;
```

Simple conditionals vectorise well. Complicated ones, or ones calling functions, usually do not.

**5. Non-contiguous memory.** Contiguous access is convenient for vector loads. Strided or indexed access may use scalar loads, wider loads with shuffles, or **gather** instructions when supported. Relative cost depends on the target, addresses and cache behaviour.

### Data layout: structure of arrays

That last point makes layout matter. An **array of structures** interleaves fields:

```
AoS: x y z x y z x y z x y z
SoA: x x x x | y y y y | z z z z
```

To update all `x` coordinates, AoS needs strided access; **structure of arrays** gives contiguous vectors. Game engines, physics codes and columnar databases use SoA for this reason.

## SIMD in the real world

Numeric libraries can combine compiled loops, CPU dispatch and SIMD. NumPy supports baseline and dispatch kernels selected for supported CPU features; use of a SIMD path depends on the operation, dtype, layout, build and runtime environment. Avoiding Python interpreter overhead is a separate benefit.

```python
import numpy as np
a = np.ones(1_000_000, dtype=np.float32)
b = np.ones(1_000_000, dtype=np.float32)
c = a + b  # SIMD path depends on build
```

## Pitfalls and trade-offs

- **Bandwidth ceiling.** Once the relevant bandwidth is saturated, faster arithmetic alone cannot remove that traffic limit. SIMD may still help reach the ceiling by changing instruction overhead or memory concurrency. Roofline is an upper bound, not proof of the actual bottleneck.
- **Portability.** Unsupported vector instructions can fault. Runtime dispatch must check CPU features *and* operating-system support for the required register state; for AVX this includes appropriate OSXSAVE/XGETBV checks. Use a supported dispatcher rather than testing one CPUID bit. Keep baseline code free of instructions unsupported on the baseline.
- **Frequency and power.** Sustained clock and vector throughput depend on the processor and workload; measure the selected target.
- **Floating-point results.** Reassociation or contraction into FMA can change results. Validate error tolerances and special-value behaviour before enabling transformations. Vectorisation itself need not reorder a reduction.
- **Short loops.** Setup, checks and tails can outweigh the gain; the threshold is workload-dependent.

> [!note] Evidence limits
> A product-by-product SIMD release history, generic speedup ranges and claims about which vector length most products use is omitted because reliable coverage of those hardware and benchmark specifics was not established in this review.

## Key takeaways
- SIMD makes one instruction work on several lanes: 4 floats in 128-bit SSE or NEON, 8 in AVX, 16 in AVX-512.
- Two 8-lane FMAs issued each cycle give a theoretical 32 FLOPs per cycle; ISA support alone does not promise that throughput.
- Compilers auto-vectorise simple loops; aliasing, loop-carried dependencies, FP reduction semantics, complex branches and scattered memory can constrain them.
- Use `restrict`, structure-of-arrays layout and vectoriser reports to help the compiler; reach for intrinsics only for hot kernels.
- SIMD speeds up compute-bound loops; memory-bound loops are limited by bandwidth instead.

## Further reading
- [Single instruction, multiple data — Wikipedia](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data)
- [Advanced Vector Extensions — Wikipedia](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions)
- [Auto-vectorization in LLVM — LLVM docs](https://llvm.org/docs/Vectorizers.html)
- [Automatic vectorization — Wikipedia](https://en.wikipedia.org/wiki/Automatic_vectorization)

- [NumPy CPU dispatch](https://numpy.org/doc/stable/reference/simd/how-it-works.html)

- [GCC optimisation options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)

- [Arm introduction to SVE](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/SVE%20programmers%20guide/102476_0001_00_en_introduction-to-sve.pdf?revision=dd9b245b-d819-43c3-8040-e69250d7b003)

- [Intel instruction extensions reference](https://www.intel.com/content/dam/develop/external/us/en/documents/319433-024-697869.pdf)
