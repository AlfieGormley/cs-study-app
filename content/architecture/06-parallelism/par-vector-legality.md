---
id: par-vector-legality
title: Compiler vectorisation: legality and data layout
level: intermediate
minutes: 3
sourceLesson: par-simd
summary: Dependencies, aliasing and numerical requirements constrain legal transformations.
---

## Letting the compiler do it: auto-vectorisation

Intrinsics target particular extensions. Auto-vectorisation lets a compiler select transformations for its target and cost model. Current Clang enables loop vectorisation at `-O2`; GCC also enables it at `-O2`, with a more conservative cost model than `-O3`. Check the actual compiler version and optimisation report. On x86, `-mavx2` enables AVX2 instructions; `-march=native` targets the build machine and may produce binaries unsuitable for other machines.

Ask the compiler what it did: `-fopt-info-vec-missed` (GCC) or `-Rpass-missed=loop-vectorize` (Clang).

### What blocks vectorisation

**1. Possible aliasing.** In a scalar array-add loop, if `a` overlaps `b` shifted by one element, one iteration may feed the next. A compiler needs a safe transformation, potentially using a runtime overlap check. The manual compute kernel above instead requires disjoint output. C's `restrict` can express exclusive access to modified objects through the relevant pointer; two read-only inputs may still alias:

```c
void add(float *restrict a,
         const float *restrict b,
         const float *restrict c,
         size_t n);
```

**2. Loop-carried dependencies.** Here each iteration needs the previous result, so lanes cannot run independently:

```c
/* Each result feeds the next iteration. */
for (i = 1; i < n; i++)
  a[i] = a[i - 1] * 0.5f + b[i];
```

**3. Floating-point reductions.** Independent partial sums change the addition order. The error can be much larger than a last-bit difference, and overflow or special values can behave differently. Reassociation requires an appropriate numerical contract; GCC's `-fassociative-math` has additional prerequisites, and `-ffast-math` relaxes several rules, not just ordering. Some targets support ordered vector reductions without reassociation. Unsigned integer addition is associative modulo its width; signed overflow is undefined in C. Legal vectorisation still depends on the target and cost model.

**4. Branches.** SIMD lanes cannot take different paths. The compiler may **if-convert** safe work into per-lane selects or masked operations. It cannot blindly evaluate both sides if that introduces invalid accesses, exceptions or observable side effects.

```c
/* Select zero for non-positive inputs. */
for (i = 0; i < n; i++)
  a[i] = b[i] > 0 ? b[i] : 0;
```

Simple conditionals can vectorise well. More complex control flow and function calls may require inlining, vector-function variants or transformations supported by the compiler and target; inspect the actual report.

**5. Strided and indexed access.** Contiguous access is convenient for vector loads. Strided or indexed access may use scalar loads, wider loads with shuffles, or **gather instructions** when supported. Relative cost depends on the target, addresses and cache behaviour.

### Data layout: structure of arrays

That last point makes layout matter. An **array of structures** interleaves fields:

```
AoS: x y z x y z x y z x y z
SoA: x x x x | y y y y | z z z z
```

To update all `x` coordinates, AoS needs strided access; **structure of arrays** gives contiguous vectors. Game engines, physics codes and columnar databases use SoA for this reason.

## Key takeaways
- Dependencies, aliasing and numerical requirements constrain legal transformations.
- Structure of arrays can make one field contiguous; compiler reports explain target-specific decisions.

## Further reading
- [LLVM vectoriser mechanisms and legality](https://llvm.org/docs/Vectorizers.html)
- [GCC optimisation contracts](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Intel basic architecture and vector instructions](https://cdrdv2.intel.com/v1/dl/getContent/671436)
- [Arm SVE execution-context lengths](https://learn.arm.com/insights/sve/)
- [NumPy CPU dispatch](https://numpy.org/doc/stable/reference/simd/how-it-works.html)
