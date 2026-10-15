---
id: par-vector-intrinsics
title: AVX intrinsics and scalar tails
level: intermediate
minutes: 3
sourceLesson: par-simd
summary: Full vectors handle groups of eight floats; the tail handles the remainder.
---

## Writing SIMD by hand: intrinsics

Compilers expose vector instructions as **intrinsics**, C functions that map almost one-to-one onto instructions. Here is an AVX array addition:

```c
#include <immintrin.h>
#include <stddef.h>

void add(float *a, const float *b,
         const float *c, size_t n) {
  size_t i = 0;
  /* Read only full eight-float groups. */
  for (; n - i >= 8; i += 8) {
    /* Load inputs; add matching lanes. */
    __m256 vb = _mm256_loadu_ps(b + i);
    __m256 vc = _mm256_loadu_ps(c + i);
    __m256 va = _mm256_add_ps(vb, vc);
    /* Store eight disjoint results. */
    _mm256_storeu_ps(a + i, va);
  }
  for (; i < n; i++)   /* scalar tail */
    a[i] = b[i] + c[i];
}
```

Precondition: each pointer provides at least n valid floats; the output range does not overlap either input range. The two read-only input ranges may overlap. Compile for an AVX-capable execution environment. These explicit intrinsics do not insert a scalar fallback for unsafe overlap.

Note the two loops. The main loop handles eight elements per iteration; the **tail loop** handles whatever is left over when n is not a multiple of 8:

```formula
N_vec = ⌊n / 8⌋
N_tail = n mod 8
N_vec = ⌊1003 / 8⌋ = 125
N_tail = 1003 mod 8 = 3
where
n: the number of array elements; 1003 in the example
N_vec: the number of main-loop iterations, each handling 8 elements
N_tail: the number of elements the scalar tail loop handles, from 0 to 7
⌊ ⌋: floor: round down to a whole number
mod: the remainder after whole-number division (1003 = 125 × 8 + 3)
8: the lane count of a 256-bit AVX register holding 32-bit floats
In words: 1,003 floats need 125 full eight-lane iterations, and the tail loop finishes the last 3 one at a time.
```

`loadu` means "unaligned load"; its performance depends on the target, alignment, cache-line and page boundaries.

The NEON version looks the same with different names: `float32x4_t`, `vld1q_f32`, `vaddq_f32`, `vst1q_f32`, four lanes at a time.

## Key takeaways
- Full vectors handle groups of eight floats; the tail handles the remainder.
- The example requires valid ranges, disjoint output and an AVX-capable execution environment.

## Further reading
- [LLVM vectoriser mechanisms and legality](https://llvm.org/docs/Vectorizers.html)
- [GCC optimisation contracts](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Intel basic architecture and vector instructions](https://cdrdv2.intel.com/v1/dl/getContent/671436)
- [Arm SVE execution-context lengths](https://learn.arm.com/insights/sve/)
- [NumPy CPU dispatch](https://numpy.org/doc/stable/reference/simd/how-it-works.html)
