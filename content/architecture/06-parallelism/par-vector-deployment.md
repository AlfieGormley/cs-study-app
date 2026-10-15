---
id: par-vector-deployment
title: Deploying and measuring vector code
level: intermediate
minutes: 3
sourceLesson: par-simd
summary: Runtime dispatch checks CPU features and required operating-system register-state support.
---

## SIMD in the real world

Numeric libraries can combine compiled loops, CPU dispatch and SIMD. NumPy supports baseline and dispatch compute kernels selected for supported CPU features; use of a SIMD path depends on the operation, dtype, layout, build and runtime environment. Avoiding Python interpreter overhead is a separate benefit.

```python
import numpy as np
a = np.ones(1_000_000, dtype=np.float32)
b = np.ones(1_000_000, dtype=np.float32)
# One result per pair; all values are 2.
# SIMD selection depends on the build.
c = a + b
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
- Runtime dispatch checks CPU features and required operating-system register-state support.
- Bandwidth, numerical semantics and short-loop overhead can limit vector gains.

## Further reading
- [LLVM vectoriser mechanisms and legality](https://llvm.org/docs/Vectorizers.html)
- [GCC optimisation contracts](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Intel basic architecture and vector instructions](https://cdrdv2.intel.com/v1/dl/getContent/671436)
- [Arm SVE execution-context lengths](https://learn.arm.com/insights/sve/)
- [NumPy CPU dispatch](https://numpy.org/doc/stable/reference/simd/how-it-works.html)
