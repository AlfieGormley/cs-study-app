---
id: ds-complex-components
title: Complex numbers as two components
level: intermediate
minutes: 5
summary: Read real and imaginary parts, magnitude, conjugation and a rotating phasor.
---

A **complex number** stores two real components in one mathematical object. The **real part** lies on a horizontal axis and the **imaginary part** lies on a perpendicular vertical axis. Imaginary does not mean erroneous or physically impossible: it names a second mathematical direction. DSP uses these pairs to retain the strength and phase of sinusoidal components.

## Two coordinates, one number

The imaginary unit is the number whose square is negative one. Engineers often write it as j; Python uses a trailing `j` in a complex literal such as `3+4j`.

```formula
j^2 = −1
z = a + jb
|z| = √(a^2 + b^2)
z_bar = a − jb
where
j: imaginary unit, whose square is −1
z: complex number; its two components share the same units, or are both unitless
a: real component of z
b: imaginary component of z
|z|: non-negative magnitude of z, in the same units as its components
√: non-negative square root
z_bar: complex conjugate of z, formed by reversing the imaginary component’s sign
In words: Treat the real and imaginary components as two perpendicular coordinates; magnitude is their distance from the origin, and conjugation reflects across the real axis.
```

For a real part of 3 and an imaginary part of 4, the magnitude is 5. The conjugate has real part 3 and imaginary part −4, and still has magnitude 5. Adding complex values adds the two real parts and the two imaginary parts separately. Do not add the component magnitudes to obtain the overall magnitude.

> [!analogy] Real-world analogy: Directions on a map
> A location three blocks east and four blocks north has two coordinates. Its straight-line distance from the starting point is five blocks.
>
> **How it maps:** The two map directions represent real and imaginary components. Reflecting north to south resembles complex conjugation.
>
> **Where it stops:** Complex multiplication has specific rotation and scaling rules; map coordinates alone do not explain all complex arithmetic.

## A rotating phasor

A **phasor** represents an amplitude and an angle together. Picture an arrow from the origin to a complex point. Its length is magnitude and its direction is phase. A rotating unit phasor can be written using cosine for the horizontal part and sine for the vertical part:

```formula
p[n] = cos(θ_n) + j sin(θ_n)
θ_n = 2πfn / F_s + φ
|p[n]| = 1
where
p: unitless complex sequence representing a rotating arrow of length one
n: any integer sample index; this sequence formula has no fixed finite upper index
cos: cosine function, taking radians and producing a unitless horizontal component
sin: sine function, taking radians and producing a unitless vertical component
θ_n: arrow angle at sample n, in radians
j: imaginary unit, whose square is −1
π: pi, about 3.14159
f: rotation frequency, in hertz (Hz)
F_s: sample rate, in samples per second
φ: starting angle, in radians
| |: complex magnitude, distance from the origin
Hz: hertz, cycles per second
In words: The arrow rotates while its horizontal and vertical projections oscillate; its magnitude stays one.
```

At one cycle per four samples, starting along the positive real axis, the phasor visits right, up, left and down. Its real part follows cosine, its imaginary part follows sine. Reversing the imaginary sign reverses the direction of rotation. Later Fourier lessons use complex weights to compare data against such rotations; no transform knowledge is needed yet.

This complete example shows Python’s component access, magnitude and conjugation. `.imag` returns the real coefficient of the imaginary unit, not a separate imaginary number.

```python
z = complex(3, 4)
print(z.real, z.imag, abs(z))
print(z.conjugate())
# 3.0 4.0 5.0
# (3-4j)
```

The zero complex number has magnitude zero but no unique direction. An angle returned for zero by software should not be treated as evidence of a meaningful physical phase.

## Key takeaways
- A complex number has real and imaginary components.
- Magnitude combines perpendicular components; conjugation flips the imaginary sign.
- A rotating phasor packages cosine and sine while retaining phase information.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH30.PDF)
