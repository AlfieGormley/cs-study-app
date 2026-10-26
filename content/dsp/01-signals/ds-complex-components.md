---
id: ds-complex-components
title: Complex numbers as two components
level: intermediate
minutes: 3
summary: Read real and imaginary parts, magnitude, conjugation and a rotating phasor.
---

A **complex number** stores two real components in one mathematical object. The **real part** lies on a horizontal axis and the **imaginary part** lies on a perpendicular vertical axis. Imaginary does not mean erroneous or physically impossible: it names a second mathematical direction. DSP uses these pairs to retain the strength and phase of sinusoidal components.

## Two coordinates, one number

The imaginary unit is the number whose square is negative one. Engineers often write it as j. Think of the components as coordinates, rather than two ordinary magnitudes to add. The **complex magnitude** is the straight-line distance from the origin. Its units are the same as the components’ units.

For a real part of 3 and an imaginary part of 4, the magnitude is 5, not 7. Adding complex values instead adds the two real parts and the two imaginary parts separately.

The **complex conjugate** keeps the real part and reverses the imaginary part’s sign. Our example becomes real part 3 and imaginary part −4. It reflects across the real axis while keeping the same magnitude. These reference expressions collect the coordinate rules:

```formula reference
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
In words: Real and imaginary components are perpendicular coordinates. Magnitude is the distance from the origin, rather than their sum. Conjugation flips the imaginary direction while preserving that distance.
```

> [!analogy] Real-world analogy: Directions on a map
> A location three blocks east and four blocks north has two coordinates. Its straight-line distance from the starting point is five blocks.
>
> **How it maps:** The two map directions represent real and imaginary components. Reflecting north to south resembles complex conjugation.
>
> **Where it stops:** Complex multiplication has specific rotation and scaling rules; map coordinates alone do not explain all complex arithmetic.

## A rotating phasor

A **phasor** represents a magnitude and a phase angle together. Picture an arrow from the origin to a complex point. Its length is magnitude and its direction is phase. When an arrow of fixed length rotates, its horizontal and vertical components change even though its magnitude does not. One component alone therefore cannot describe the complete arrow.

At one cycle per four samples, starting along the positive real axis, the phasor visits right, up, left and down. Its real part follows cosine, its imaginary part follows sine. Reversing the imaginary sign reverses the direction of rotation. Later Fourier lessons use complex weights to compare data against such rotations; no transform knowledge is needed yet.

The zero complex number has magnitude zero but no unique direction. An angle returned for zero by software should not be treated as evidence of a meaningful physical phase.

## Key takeaways
- A complex number has real and imaginary components.
- Magnitude combines perpendicular components; conjugation flips the imaginary sign.
- A rotating phasor packages cosine and sine while retaining phase information.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH30.PDF)
