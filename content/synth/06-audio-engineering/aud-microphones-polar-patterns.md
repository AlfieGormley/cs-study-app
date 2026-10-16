---
id: aud-microphones-polar-patterns
title: Read microphone patterns and their nulls
level: intermediate
minutes: 5
summary: Ideal first-order patterns combine omnidirectional and figure-eight responses.
sourceLesson: aud-microphones
---

## Polar patterns

How a mic responds to sound from different directions depends on how the diaphragm is exposed:

- **Pressure microphones** (diaphragm open only at the front, sealed behind) respond to pressure itself, which has no direction: **omnidirectional**.
- **Pressure-gradient** mics (open at front and back) respond to the *difference* in pressure between the two sides. Sound from the side reaches both sides equally, giving a null: **figure-8**.
- Combining the two (or using an acoustic delay network behind the diaphragm) gives the **cardioid family**.

All the common ("first-order") patterns are a mix of an omni part, which is the same in every direction, and a figure-8 part, which follows the cosine of the angle. One formula covers the whole family; only the mix changes:

```formula
r(θ) = A + (1 − A) cos(θ)
where
r(θ): the microphone's relative sensitivity to sound arriving from angle θ, as a fraction of its on-axis sensitivity; 1 means as sensitive as straight ahead, 0 means a null (no pickup), and a negative value means a lobe that picks up with inverted polarity
r: the relative sensitivity (see r(θ))
θ: theta, the angle between the sound's direction and the front axis of the mic, in degrees (°); 0° is straight ahead, 90° is the side, 180° is directly behind
A: the omni share of the mix, a pure number from 0 to 1; A = 1 is omni, A = 0 is figure-8, A = 0.5 is cardioid, about 0.37 is supercardioid and 0.25 is hypercardioid
cos: cosine, a function that is 1 at 0°, 0 at 90° and −1 at 180°
In words: the pickup in any direction is the fixed omni part plus the figure-8 part scaled by the cosine of the angle. Lowering A narrows the front but grows a rear lobe.
```

To compare directions you convert the ratio r into decibels relative to the front. Setting r to zero and solving gives the angle of the null:

```formula
L(θ) = 20 log_10(|r(θ)|)
cos(θ_null) = −A / (1 − A)
θ_null = arccos(−A / (1 − A))
where
L(θ): the pickup level from angle θ relative to straight ahead, in decibels (dB); 0 dB is the on-axis level, −6 dB is half the voltage
r(θ): the relative sensitivity from the formula above, a pure number
r: the relative sensitivity (see r(θ))
θ: theta, the angle from the front axis, in degrees (°)
θ_null: the angle at which the mic picks up nothing, in degrees (°)
A: the omni share of the mix, from 0 to 1
log_10: the base-10 logarithm; 20 × log_10 is used because r is a voltage (amplitude) ratio
|r(θ)|: the size of r ignoring its sign (absolute value), because a rear lobe with inverted polarity is still heard
cos: cosine
arccos: the inverse cosine: the angle whose cosine is the given number
dB: decibel, a logarithmic unit for a ratio
In words: turn the sensitivity ratio into decibels to compare directions, and the null sits where the cosine term exactly cancels the omni part.
```

The logarithmic pickup formula applies only where the sensitivity magnitude is nonzero; at an ideal null its limiting level is negative infinity. A real microphone has finite rejection. The null-angle expression applies only when the omni share is at most one half and less than one; a pure omni has no null.

Worked through for a cardioid with omni share 0.5 and a hypercardioid with omni share 0.25:

```formula
r_c(90°) = 0.5 + 0.5 × 0 = 0.5
L_c(90°) = 20 log_10(0.5) ≈ −6.0 dB
r_c(180°) = 0.5 + 0.5 × (−1) = 0
cos(θ_null) = −0.25 / 0.75 = −1/3
θ_null = arccos(−1/3) ≈ 109.5°
r_h(180°) = 0.25 − 0.75 = −0.5
L_h(180°) = 20 log_10(0.5) ≈ −6.0 dB
where
r_c: the cardioid's (A = 0.5) relative sensitivity at the angle in brackets, a pure number; 90° is the side, 180° directly behind
r_h: the hypercardioid's (A = 0.25) relative sensitivity at the angle in brackets, a pure number
L_c: the cardioid's pickup at that angle relative to the front, in decibels (dB)
L_h: the hypercardioid's pickup at that angle relative to the front, in decibels (dB)
θ_null: the hypercardioid's null angle, in degrees (°)
cos: cosine (cos 90° = 0, cos 180° = −1)
arccos: inverse cosine
log_10: base-10 logarithm
dB: decibel
≈: approximately equal to (the result is rounded)
In words: a cardioid is 6 dB down at the side and silent behind; a hypercardioid's nulls sit at about 110°, and its rear lobe is only 6 dB down (with inverted polarity).
```

The same sums in Python, for all three directional patterns (the code puts the absolute value in for you):

```python
import math

def rel_db(a, deg):
    # The pattern uses degrees; cos needs
    # rad.
    r = a + (1 - a) * math.cos(
        math.radians(deg))
    return 20 * math.log10(abs(r))

pats = {"cardioid": 0.5,
        "super": 0.366,
        "hyper": 0.25}
for name, a in pats.items():
    null = math.degrees(
        math.acos(-a / (1 - a)))
    print(f"{name}: 90deg "
          f"{rel_db(a, 90):5.1f} dB,"
          f" null {null:5.1f} deg")
```

```
cardioid: 90deg  -6.0 dB, null 180.0 deg
super: 90deg  -8.7 dB, null 125.3 deg
hyper: 90deg -12.0 dB, null 109.5 deg
```

| Pattern | Side (90°) | Null |
|---|---|---|
| Omni | 0 dB | none |
| Cardioid | −6 dB | 180° (rear) |
| Supercardioid | ≈ −8.7 dB | ≈ 125° |
| Hypercardioid | −12 dB | ≈ 110° |
| Figure-8 | null | 90° |

Super- and hypercardioids are narrower at the front but have a **rear lobe** (a hypercardioid is only −6 dB directly behind). That matters for stage monitors (the sound-system units): put a wedge at a cardioid's 180° null, but at the 110–125° nulls of a hyper- or supercardioid.

Real microphones only follow these shapes approximately. Their directionality can change substantially with frequency; a pressure-gradient design can retain low-frequency directionality, while a pressure microphone becomes more directional at high frequencies as its size matters. Check the polar plots in the datasheet.

## Key takeaways
- Ideal first-order patterns combine omnidirectional and figure-eight responses.
- A cardioid’s rear null differs from the angled nulls of hypercardioid and supercardioid patterns.
- Measured polar plots vary with frequency and determine practical placement.

## Further reading
- [Microphone technology — DPA](https://www.dpamicrophones.com/mic-university/technology/microphone-technology-the-essentials/)
- [U 87 Ai technical data — Neumann](https://www.neumann.com/en-en/products/microphones/u-87-ai/)
- [Phantom power — Schoeps](https://schoeps.de/en/knowledge/knowledge-base/technical-basics/phantom-power-p48p12.html)
- [Three-to-one rule — DPA](https://www.dpamicrophones.com/dict/3-1-rule/)
