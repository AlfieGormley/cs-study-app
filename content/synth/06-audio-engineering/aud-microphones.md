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

All the first-order patterns follow one formula, where A sets the mix of omni and figure-8:

```
r(theta) = A + (1 - A) * cos(theta)
```

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

- **mV/Pa**, or
- **dBV/Pa** = 20·log10(sensitivity in V/Pa).

| Mic (manufacturer's figures) | mV/Pa | dBV/Pa |
|---|---|---|
| Shure SM58 (dynamic) | 1.85 | −54.5 |
| Neumann U 87 Ai, cardioid | 28 | ≈ −31 |

(Shure publishes both −54.5 dBV/Pa and 1.85 mV; strictly, −54.5 dBV/Pa is 1.88 mV/Pa, so the two figures differ slightly through rounding. Supercardioid definitions also vary a little between sources; A = 0.366 is one common choice. Specs checked October 2026: confirm against current datasheets.)

The difference is 20·log10(28 / 1.85) ≈ **23.6 dB**: the dynamic needs about 24 dB more preamp gain for the same output. Gain raises signal and input noise together. For quiet sources, compare microphone sensitivity, its own noise and the preamp’s equivalent input noise; a low-noise condenser often performs well.

### Self-noise

A condenser's electronics produce some noise even in a silent room. **Self-noise** (or "equivalent noise level") is quoted as the SPL that would produce the same output, usually A-weighted (dB-A). Neumann specifies the U 87 Ai's self-noise as **12 dB-A** in cardioid. Below about 10 dB-A is very quiet; above about 20 dB-A can become audible on quiet sources.

Passive dynamics and ribbons have no active electronics, but their winding and transformer resistance still generate thermal noise. That noise and the preamp’s input noise both contribute to the recorded noise floor.

### Maximum SPL and dynamic range

Max SPL is the level at which distortion reaches a stated figure (often 0.5% or 1% THD). Neumann gives **117 dB SPL** for the U 87 Ai (127 dB with its pre-attenuation pad). The dynamic range is the gap between self-noise and max SPL: about 117 − 12 = 105 dB.

## Phantom power (P48)

Condenser microphones are powered through the same balanced cable that carries their signal. **IEC 61938** defines **P48**:

- **+48 V** fed through two matched **6.81 kΩ** resistors, one to each signal conductor (pins 2 and 3 of an XLR), with the shield (pin 1) as the return.
- Closely matched feed resistors help preserve the impedance balance of the line.
- The standard allows up to **10 mA** per microphone. Lower-voltage P12 and P24 variants also exist.

The equal DC on the signal wires is common-mode, so it does not appear across an ideal floating dynamic coil. A preamp still needs suitable DC blocking, voltage ratings and transient protection: common-mode rejection alone does not make an arbitrary balanced input safe at 48 V.

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

Why it works: by the inverse square law, at three times the distance the leakage is 20·log10(3) ≈ **9.5 dB** lower. A copy 9.5 dB down can only change the sum by about +2.5 dB / −3.5 dB at its peaks and notches, instead of +6 dB and total cancellation for equal levels.

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
- First-order patterns follow A + (1 − A)·cos θ: cardioid is −6 dB at the side with a rear null; hyper- and supercardioids have nulls near 110° and 125° and rear lobes.
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
