---
id: aud-microphones
title: Microphones
level: intermediate
minutes: 16
summary: How dynamic, condenser and ribbon microphones turn pressure into voltage, polar patterns and the maths behind them, proximity effect, reading sensitivity and self-noise specifications, 48 V phantom power (IEC 61938), and placement including the 3:1 rule.
---

A moving-coil microphone resembles a moving-coil loudspeaker run backwards: a light diaphragm moved by sound pressure, connected to something that turns motion into voltage. The way it makes that conversion decides its sensitivity, noise, ruggedness and whether it needs power. The way sound reaches the diaphragm decides its directional pattern.

Even if you mostly record your synth by plugging it straight in (lesson 8's DI box), you'll mic amplifiers, voices and rooms, and you'll need to read microphone specifications.

## Three ways to make a voltage

### Dynamic (moving coil)

A small coil of wire is glued to the diaphragm and sits in the gap of a permanent magnet. Sound moves the diaphragm, the coil moves through the magnetic field, and **electromagnetic induction** generates a voltage proportional to its velocity.

- A traditional passive moving-coil mic needs no power; models with built-in active electronics are exceptions.
- Rugged and tolerant of very high SPL (kick drums, guitar cabs, vocals on stage).
- The coil adds mass, so transient and high-frequency detail are usually less than a condenser's.
- Low output: typically around 1–3 mV per pascal. Needs plenty of preamp gain.

The Shure SM58 is the classic example.

### Condenser (capacitor)

The diaphragm is one plate of a **capacitor**; a fixed **backplate** is the other. Sound changes the gap, so the capacitance changes. With a fixed charge on the capacitor (from a polarising voltage, or permanently stored in an **electret** material), a change in capacitance gives a change in voltage.

- The capsule has an extremely high impedance, so every condenser contains an **impedance converter** (a small amplifier). That needs power: usually phantom power, sometimes a battery or a dedicated supply for valve models.
- The diaphragm is very light, so condensers capture fast transients and high-frequency detail.
- Often higher output (for example 10–30 mV/Pa). A low-noise condenser can give a quieter recording of a quiet source, but compare the actual microphone and preamp specifications; the operating principle alone does not guarantee lower noise or lower maximum SPL.

### Ribbon

A very thin corrugated metal ribbon hangs in a magnetic field. Sound moves the ribbon, and induction generates a voltage, as in a dynamic mic. The ribbon has a tiny output and very low impedance, so passive ribbons use a step-up transformer.

- Open at front and back, a ribbon naturally has a **figure-8** pattern.
- Smooth, often darker high end.
- Physically fragile: a blast of air (wind, a kick drum port, blowing into it) can stretch the ribbon.

> [!warning] Ribbons and phantom power
> A correctly wired balanced cable puts phantom voltage equally on both signal pins, so in principle a passive ribbon sees no net DC. Damage can still happen with a faulty or miswired cable, with unbalanced adapters, or when hot-plugging with phantom on, because the pins don't make contact at the same instant. Switch phantom power **off** before connecting a passive ribbon (or anything that doesn't need it). Some modern "active" ribbons need phantom: follow the manufacturer's manual.

## Polar patterns

How a mic responds to sound from different directions depends on how the diaphragm is exposed:

- **Pressure** mics (diaphragm open only at the front, sealed behind) respond to pressure itself, which has no direction: **omnidirectional**.
- **Pressure-gradient** mics (open at front and back) respond to the *difference* in pressure between the two sides. Sound from the side reaches both sides equally, giving a null: **figure-8**.
- Combining the two (or using an acoustic delay network behind the diaphragm) gives the **cardioid family**.

All the common ("first-order") patterns are a mix of an omni part, which is the same in every direction, and a figure-8 part, which follows the cosine of the angle. One formula covers the whole family; only the mix changes:

```formula
r(θ) = A + (1 − A) × cos(θ)
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
L(θ) = 20 × log_10(|r(θ)|)
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

Worked through for a cardioid (A = 0.5) and a hypercardioid (A = 0.25):

```formula
r_c(90°) = 0.5 + 0.5 × 0 = 0.5
L_c(90°) = 20 × log_10(0.5) ≈ −6.0 dB
r_c(180°) = 0.5 + 0.5 × (−1) = 0
cos(θ_null) = −0.25 / 0.75 = −1/3
θ_null = arccos(−1/3) ≈ 109.5°
r_h(180°) = 0.25 − 0.75 = −0.5
L_h(180°) = 20 × log_10(0.5) ≈ −6.0 dB
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

Super- and hypercardioids are narrower at the front but have a **rear lobe** (a hypercardioid is only −6 dB directly behind). That matters for stage monitors (lesson 8): put a wedge at a cardioid's 180° null, but at the 110–125° nulls of a hyper- or supercardioid.

Real microphones only follow these shapes approximately, and usually become less directional at low frequencies and more directional at high frequencies. Check the polar plots in the datasheet.

## Proximity effect

Directional (pressure-gradient) mics have a **bass boost when the source is very close**, within a few centimetres to tens of centimetres. Close to a small source, the pressure difference between the front and back of the diaphragm contains an extra component that is relatively strongest at low frequencies. The closer the source, the bigger the boost.

- Singers use it ("eating the mic" for a warm, big voice).
- It causes boomy, muddy recordings when you didn't want it.
- **Omnidirectional (pure pressure) mics have no proximity effect.**
- Many directional mics have a bass-cut switch to compensate.

## Reading the specifications

### Sensitivity

The output voltage for a given sound pressure, normally at 1 kHz and **1 Pa (94 dB SPL)**:

- **mV/Pa**: millivolts of output per pascal of sound pressure, or
- **dBV/Pa**: the same figure in decibels relative to 1 volt per pascal.

Converting between the two is a voltage-ratio decibel calculation:

```formula
S_dBV = 20 × log_10(S / 1 V/Pa)
S_dBV = 20 × log_10(0.028 V/Pa / 1 V/Pa)
S_dBV ≈ −31.1 dBV/Pa
where
S_dBV: the sensitivity in decibels relative to 1 volt per pascal (dBV/Pa); always negative for real mics, and less negative means more output
S: the sensitivity as a voltage ratio, in volts per pascal (V/Pa); here 28 mV/Pa = 0.028 V/Pa (a Neumann U 87 Ai)
log_10: the base-10 logarithm
V: volt, the unit of voltage
Pa: pascal, the unit of pressure; 1 Pa is about 94 dB SPL
dBV: decibels relative to 1 volt
≈: approximately equal to (the result is rounded)
In words: sensitivity in dBV/Pa is 20 times the base-10 log of the output voltage per pascal; 28 mV/Pa comes out at about −31 dBV/Pa.
```

| Mic (manufacturer's figures) | mV/Pa | dBV/Pa |
|---|---|---|
| Shure SM58 (dynamic) | 1.85 | −54.5 |
| Neumann U 87 Ai, cardioid | 28 | ≈ −31 |

(Shure publishes both −54.5 dBV/Pa and 1.85 mV; strictly, −54.5 dBV/Pa is 1.88 mV/Pa, so the two figures differ slightly through rounding. Supercardioid definitions also vary a little between sources; A = 0.366 is one common choice. Specs checked October 2026: confirm against current datasheets.)

How much more preamp gain does the less sensitive mic need for the same output? Take the ratio of the two sensitivities and convert it to decibels:

```formula
G = 20 × log_10(S_A / S_B)
G = 20 × log_10(28 mV/Pa / 1.85 mV/Pa)
G = 20 × log_10(15.14)
G ≈ 23.6 dB
where
G: the extra preamp gain mic B needs to match mic A's output, in decibels (dB)
S_A: the sensitivity of the more sensitive mic (here the U 87 Ai), in millivolts per pascal (mV/Pa)
S_B: the sensitivity of the less sensitive mic (here the SM58), in mV/Pa
log_10: the base-10 logarithm; 20 × log_10 because these are voltage ratios
mV: millivolt, a thousandth of a volt
Pa: pascal, the unit of pressure
dB: decibel
≈: approximately equal to (the result is rounded)
In words: the condenser puts out about 15 times the voltage, which is about 23.6 dB, so the dynamic needs about 24 dB more preamp gain.
```

So the dynamic needs about **24 dB** more preamp gain for the same output. Gain raises signal and input noise together. For quiet sources, compare microphone sensitivity, its own noise and the preamp’s equivalent input noise; a low-noise condenser often performs well.

### Self-noise

A condenser's electronics produce some noise even in a silent room. **Self-noise** (or "equivalent noise level") is quoted as the SPL that would produce the same output, usually A-weighted (dB-A). Neumann specifies the U 87 Ai's self-noise as **12 dB-A** in cardioid. Below about 10 dB-A is very quiet; above about 20 dB-A can become audible on quiet sources.

Passive dynamics and ribbons have no active electronics, but their winding and transformer resistance still generate thermal noise. That noise and the preamp’s input noise both contribute to the recorded noise floor.

### Maximum SPL and dynamic range

Max SPL is the level at which distortion reaches a stated figure (often 0.5% or 1% THD). Neumann gives **117 dB SPL** for the U 87 Ai (127 dB with its pre-attenuation pad). The dynamic range is the gap between self-noise and max SPL:

```formula
DR = L_max − L_noise
DR = 117 dB SPL − 12 dB SPL = 105 dB
where
DR: the microphone's dynamic range, in decibels (dB): how far the loudest clean sound is above its own noise
L_max: the maximum SPL, the sound level at which distortion reaches the stated limit, in dB SPL
L_noise: the self-noise expressed as an equivalent sound level, in dB SPL (A-weighted here)
dB: decibel
SPL: sound pressure level, measured relative to 20 µPa
In words: subtract the noise floor from the overload point; both are already in decibels, so subtraction gives the range.
```

Because the self-noise figure is A-weighted, this is an approximate, A-weighted range; with the pad engaged the top end rises to 127 dB SPL.

## Phantom power (P48)

Condenser microphones are powered through the same balanced cable that carries their signal. **IEC 61938** defines **P48**:

- **+48 V** fed through two matched **6.81 kΩ** resistors, one to each signal conductor (pins 2 and 3 of an XLR), with the shield (pin 1) as the return.
- Closely matched feed resistors help preserve the impedance balance of the line.
- The standard allows up to **10 mA** per microphone. Lower-voltage P12 and P24 variants also exist.

The equal DC on the signal wires is common-mode, so it does not appear across an ideal floating dynamic coil. A preamp still needs suitable DC blocking, voltage ratings and transient protection: common-mode rejection alone does not make an arbitrary balanced input safe at 48 V.

The mic draws its current through both feed resistors at once. Two equal resistors side by side (in parallel) act like one of half the value, and the voltage lost across them follows Ohm's law:

```formula
R_feed = 6810 Ω / 2 = 3405 Ω
V_mic = V_s − I × R_feed
V_mic = 48 V − 0.010 A × 3405 Ω
V_mic = 48 V − 34.05 V ≈ 14.0 V
where
R_feed: the combined resistance of the two 6.81 kΩ feed resistors in parallel, in ohms (Ω)
V_mic: the DC voltage left at the microphone, in volts (V)
V_s: the phantom supply voltage, 48 V for P48
I: the current the microphone draws, in amperes (A); here 10 mA = 0.010 A, the maximum the standard allows
Ω: ohm, the unit of resistance
V: volt
A: ampere (amp), the unit of current
≈: approximately equal to (the result is rounded)
In words: the more current the mic draws, the more voltage is dropped in the feed resistors, so a hungry mic sees much less than 48 V.
```

The same calculation for three currents, in Python:

```python
R_feed = 6810 / 2     # two in parallel
for i_ma in (0.8, 5, 10):
    v = 48 - i_ma / 1000 * R_feed
    print(f"{i_ma:>4} mA: "
          f"{v:5.1f} V at mic")
```

```
 0.8 mA:  45.3 V at mic
   5 mA:  31.0 V at mic
  10 mA:  14.0 V at mic
```

The feed resistors limit what the mic can draw: a low-current mic like the U 87 Ai (0.8 mA per Neumann) sees nearly the full 48 V; a hungry one sees much less. A supply that can't deliver enough current makes some mics distort earlier.

> [!warning] Phantom power and your synth
> As module 5 said, keep phantom **off** on any channel your synth or other line-level gear is plugged into. Phantom is for microphones and DI boxes designed for it.

## Placement basics

- **Distance controls the direct-to-room balance.** Close placement gives more direct sound, less room, more proximity effect and more level variation as the performer moves. Further away captures more of the room.
- **Angle controls tone.** On a guitar cab, the centre of the cone is brighter; towards the edge it's darker. Small moves matter.
- **Use the nulls.** Aim the null of a directional mic at what you *don't* want (a monitor, a neighbouring drum).
- **Mind reflections.** A music stand or desk near the mic adds a reflection a few milliseconds late, which comb-filters the sound.

### The 3:1 rule

When several mics are open at once, a source reaches its own mic and, more weakly and later, its neighbours. When the signals are mixed, the delayed copy comb-filters the direct one. The **3:1 rule** says the distance *between* mics should be at least **three times** the distance from each mic to its source.

Why it works: by the inverse square law, sound pressure falls in proportion to distance, so the leakage level drops by:

```formula
L_leak = 20 × log_10(d_far / d_near)
L_leak = 20 × log_10(3 × d / d)
L_leak = 20 × log_10(3) ≈ 9.5 dB
where
L_leak: how far the leaked copy is below the direct sound, in decibels (dB)
d_far: the distance from the source to the neighbouring mic, in metres (m)
d_near: the distance from the source to its own mic, in metres (m)
d: the source-to-own-mic distance; the 3:1 rule makes d_far at least 3 × d
log_10: the base-10 logarithm; 20 × log_10 because pressure is an amplitude
dB: decibel
m: metre
≈: approximately equal to (the result is rounded)
In words: three times further away means about a third of the pressure, which is about 9.5 dB quieter.
```

When a copy that much quieter is mixed with the direct sound, it can only nudge the sum up or down a little:

```formula
g = 10^{−L_leak/20} = 10^{−9.5/20} ≈ 0.335
L_peak = 20 × log_10(1 + g) ≈ +2.5 dB
L_notch = 20 × log_10(1 − g) ≈ −3.5 dB
where
g: the leaked copy's amplitude as a fraction of the direct sound, a pure number
L_leak: how far the leak is below the direct sound, in decibels (dB); here 9.5 dB
L_peak: the biggest boost, at frequencies where the copy arrives in phase, in dB
L_notch: the deepest cut, at frequencies where the copy arrives out of phase, in dB
log_10: the base-10 logarithm
dB: decibel
≈: approximately equal to (the result is rounded)
In words: convert the 9.5 dB gap back to an amplitude fraction, then add or subtract it from 1 to find the worst peak and notch.
```

That's about +2.5 dB / −3.5 dB, instead of +6 dB and total cancellation when the two copies are equal (g = 1).

```diagram
  src A      src B
   |          |
  0.3 m      0.3 m
   |          |
  mic A ---- mic B
     >= 0.9 m apart
```

It's a rule of thumb that assumes omni-like pickup and similar levels. Directional mics aimed well, or very different source levels, change the numbers.

## Key takeaways
- Dynamic mics use a coil in a magnet (rugged, no power); condensers use a varying capacitor with active electronics (often sensitive; noise depends on design; need power); ribbons use a thin ribbon in a magnet (figure-8, fragile).
- First-order patterns are a fixed mix of omni and figure-8 pickup: cardioid is −6 dB at the side with a rear null; hyper- and supercardioids have nulls near 110° and 125° and rear lobes.
- Directional mics show proximity effect (bass boost close up); omnis don't.
- Sensitivity is quoted at 94 dB SPL (1 Pa); 28 mV/Pa vs 1.85 mV/Pa is about 24 dB of extra preamp gain needed.
- P48 is +48 V through matched 6.81 kΩ resistors on both signal pins, up to 10 mA (IEC 61938). Keep it off for line-level gear and passive ribbons.
- The 3:1 rule keeps leakage about 9.5 dB down so comb filtering stays mild.

## Further reading
- [Microphone — Wikipedia](https://en.wikipedia.org/wiki/Microphone)
- [Microphones — HyperPhysics](http://hyperphysics.phy-astr.gsu.edu/hbase/Audio/mic.html)
- [Proximity effect (audio) — Wikipedia](https://en.wikipedia.org/wiki/Proximity_effect_(audio))
- [Ribbon microphone — Wikipedia](https://en.wikipedia.org/wiki/Ribbon_microphone)
- [Phantom power — Wikipedia](https://en.wikipedia.org/wiki/Phantom_power)
- [U 87 Ai technical data — Neumann](https://www.neumann.com/en-en/products/microphones/u-87-ai/)
- [SM58 specifications — Shure](https://content-files.shure.com/publications/specSheet/en/sm58-spec-sheet.pdf)
- [Microphone and preamp noise — Neumann](https://www.neumann.com/fr-lu/will-a-better-preamp-give-you-lower-noise/)
- [Preamp input and phantom protection — THAT Corporation](https://thatcorp.com/datashts/dn140.pdf)
- [How to mic a choir (3:1 spacing) — Shure](https://www.shure.com/en-US/performance-production/louder/how-to-mic-a-choir)
- [3:1 rule — DPA Microphones](https://www.dpamicrophones.com/dict/3-1-rule/)
