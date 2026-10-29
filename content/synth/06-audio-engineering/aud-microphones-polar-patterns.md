---
id: aud-microphones-polar-patterns
title: Read microphone patterns and their nulls
level: intermediate
minutes: 4
summary: Ideal first-order patterns combine omnidirectional and figure-eight responses.
sourceLesson: aud-microphones
---

## Polar patterns

How a mic responds to sound from different directions depends on how the diaphragm is exposed:

- **Pressure microphones** (diaphragm open only at the front, sealed behind) respond to pressure itself, which has no direction: **omnidirectional**.
- **Pressure-gradient** mics (open at front and back) respond to the *difference* in pressure between the two sides. Sound from the side reaches both sides equally, giving a null: **figure-8**.
- Combining the two (or using an acoustic delay network behind the diaphragm) gives the **cardioid family**.

> [!analogy] Real-world analogy: a barometer and a swinging door
> A barometer reports the air pressure in the room; it neither knows nor cares which way the wind blows. A light swinging door, open on both sides, only moves when the push on one face differs from the push on the other: a draught straight through swings it, while a draught sliding past along its face leaves it still.
>
> **How it maps:** The barometer is a pressure (omnidirectional) microphone. The door is a pressure-gradient diaphragm, open front and back: sound from the front or back pushes it, while sound from the side pushes both faces equally and produces the figure-8's side null. Mixing the two behaviours gives the cardioid family.
>
> **Where it stops:** A door responds to steady wind; a diaphragm responds to tiny, rapid pressure changes, and the size of the front-to-back difference depends on frequency and distance. Real cardioids often build the mix with an acoustic delay path behind one diaphragm rather than two separate parts.

All the common ("first-order") patterns are a mix of an omni part, which is the same in every direction, and a figure-8 part, which follows the cosine of the angle. One relationship covers the whole family; only the mix changes:

```formula essential
r(θ) = A + (1 − A) cos(θ)
where
r(θ): the microphone's relative sensitivity to sound arriving from angle θ, as a fraction of its on-axis sensitivity; 1 means as sensitive as straight ahead, 0 means a null (no pickup), and a negative value means a lobe that picks up with inverted polarity
r: the relative sensitivity (see r(θ))
θ: theta, the angle between the sound's direction and the front axis of the mic, in degrees (°); 0° is straight ahead, 90° is the side, 180° is directly behind
A: the omni share of the mix, a pure number from 0 to 1; A = 1 is omni, A = 0 is figure-8, A = 0.5 is cardioid, about 0.37 is supercardioid and 0.25 is hypercardioid
cos: cosine, a function that is 1 at 0°, 0 at 90° and −1 at 180°
In words: the pickup in any direction is the fixed omni part plus the figure-8 part scaled by the cosine of the angle. Lowering A narrows the front but grows a rear lobe.
```

Read it at three landmark angles:

- **At the side (90°)** the cosine is zero, so only the omni share remains. A cardioid (half omni) keeps half its voltage there: about −6 dB.
- **Directly behind (180°)** the figure-8 part is fully negative. For a cardioid it exactly cancels the omni half, giving the rear null. With less omni (super- and hypercardioid), the figure-8 part wins, leaving a **rear lobe** of inverted polarity: a hypercardioid is only about 6 dB down directly behind.
- **The null** sits wherever the figure-8 part exactly cancels the omni part. Less omni moves it forward from 180°: about 125° for a supercardioid, about 110° for a hypercardioid and 90° for a figure-8.

```formula reference
θ_null = arccos(−A / (1 − A))
where
θ_null: the angle at which the ideal pattern picks up nothing, in degrees (°), measured from the front axis
A: the omni share of the mix, a pure number; the expression applies only for A at most 0.5, since patterns with more omni have no null
arccos: the inverse cosine: the angle whose cosine is the given number
In words: For an ideal first-order microphone the null sits where the figure-8 part exactly cancels the omni part; with less omni in the mix, the null swings forward from directly behind towards the sides.
```

| Pattern | Side (90°) | Null |
|---|---|---|
| Omni | 0 dB | none |
| Cardioid | −6 dB | 180° (rear) |
| Supercardioid | ≈ −8.7 dB | ≈ 125° |
| Hypercardioid | −12 dB | ≈ 110° |
| Figure-8 | null | 90° |

Supercardioid definitions vary a little between sources; the table uses an omni share of 0.366, one common choice. An ideal null is complete silence; a real microphone has finite rejection there.

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
