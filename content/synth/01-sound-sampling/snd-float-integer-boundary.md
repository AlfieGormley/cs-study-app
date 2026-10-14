---
id: snd-float-integer-boundary
title: Float headroom and integer conversion
level: intermediate
minutes: 3
summary: Keep internal float headroom and convert safely at fixed-format boundaries.
sourceLesson: snd-sampling
---

## The −1..1 convention and floating point

Inside most audio software, samples are **floating-point numbers where ±1.0 means full scale**. The converter's maximum output corresponds to 1.0. This convention lets the same code work whatever bit depth the hardware uses.

Why floats internally?

- **Headroom.** A float can hold 3.7 or −12.0 without trouble. Mixing several voices can exceed 1.0 mid-chain and be scaled down later without clipping; normal floating-point rounding still applies. Integers would overflow or clip.
- **Resolution where it matters.** A 32-bit float has a 24-bit significand plus an exponent. Quiet signals in the normal range keep their relative precision, because the exponent scales with the value; subnormal values lose significant bits.
- **Simple maths.** Gain is a multiply; mixing is an add.

Integer and **fixed-point arithmetic** formats still matter at the edges: WAV files, converter interfaces, and microcontrollers without a floating-point unit. The conversion at the boundary is where bugs live:

```python
import numpy as np
x = np.array([0.5, -0.25, 1.0, -1.0, 1.7])
r = np.clip(np.round(x * 32767),
            -32768, 32767)
# Cast only after rounding and clipping.
i16 = r.astype(np.int16)
print(i16)
# Decode using a different scale: a loss.
y = i16 / 32768
print(np.round(y, 5).tolist())
```

```text
[ 16384  -8192  32767 -32767  32767]
[0.5, -0.25, 0.99997, -0.99997, 0.99997]
```

Three things to notice:

1. **1.7 was clipped** to 32767. Over-range floats must be clipped at conversion, never cast directly. In C and C++, converting a float to an integer type that can't hold its value is undefined behaviour. In practice you may get a wrapped value or, on x86, the "integer indefinite" value −2,147,483,648: either way, a loud crack. NumPy is no safer: in testing, `np.array([1.7 * 32767]).astype(np.int16)` gave −9833, silently.
2. **Asymmetry.** Integers run from −32768 to +32767, so full scale isn't symmetric. Libraries choose 32767 or 32768 as the scale factor.
3. **Inconsistent scale factors.** Here the code multiplied by 32767 but divided by 32768, so a round trip shrinks the signal very slightly. Pick one convention and use it both ways.

## Pitfalls

- **Casting instead of clipping** at float-to-integer conversion.
- **Denormals.** Float values extremely close to zero (subnormals, or denormals) are much slower to process on some processors: some x86 instructions on some processors need a slow assist, costing tens or hundreds of cycles. The penalty depends on the processor, instruction and floating-point mode; benchmark the target rather than assuming a fixed cost. Decaying filters and reverbs can produce them. The usual fixes are to switch on the CPU's flush-to-zero (and denormals-are-zero) mode for the audio thread, as many audio frameworks do, or to add a tiny offset or noise so the values never get that small.

## Key takeaways

- With floats, ±1 is nominal full scale and intermediate results can exceed it.
- Clamp over-range values before integer conversion and use consistent scale factors.
- Float precision follows the signal’s scale, but subnormal values can have processor-specific performance costs.

## Further reading

- [Single-precision floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
- [Subnormal number — Wikipedia](https://en.wikipedia.org/wiki/Subnormal_number)
- [Subnormal numbers — Intel documentation](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2024-2/subnormal-numbers.html)
- [Floating-to-integer conversion — C++ standard draft](https://eel.is/c++draft/conv.fpint)
