---
id: aud-microphones-transducers
title: How microphone types produce voltage
level: intermediate
minutes: 4
summary: Moving-coil and ribbon microphones generate voltage by electromagnetic induction.
sourceLesson: aud-microphones
---

A moving-coil microphone resembles a moving-coil loudspeaker run backwards: a light diaphragm moved by sound pressure, connected to something that turns motion into voltage. The way it makes that conversion decides its sensitivity, noise, ruggedness and whether it needs power. The way sound reaches the diaphragm decides its directional pattern.

Even if you mostly record your synth by plugging it straight in (the sound-system units’ DI box), you'll mic amplifiers, voices and rooms, and you'll need to read microphone specifications.

## Three ways to make a voltage

### Dynamic (moving coil)

A small coil of wire is glued to the diaphragm and sits in the gap of a permanent magnet. Sound moves the diaphragm, the coil moves through the magnetic field, and **electromagnetic induction** generates a voltage proportional to its velocity.

- A traditional passive moving-coil mic needs no power; models with internal active electronics are exceptions.
- Rugged and tolerant of very high SPL (kick drums, guitar cabs, vocals on stage).
- The coil adds mass, so transient and high-frequency detail are usually less than a condenser's.
- Low output: typically around 1–3 mV per pascal. Needs plenty of preamp gain.

The Shure SM58 is the classic example.

### Condenser (capacitor)

The diaphragm is one plate of a **capacitor**; a fixed **backplate** is the other. Sound changes the gap, so the capacitance changes. A conventional capsule with an external polarising supply is charged through a very large resistance, so charge is approximately constant over the relevant audio timescale. An **electret** supplies a persistent electric polarisation. Changing capacitance then changes the capsule voltage; the readout electronics and capsule design still matter.

- The capsule has an extremely high impedance, so a conventional studio condenser microphone uses an **impedance converter** (a small amplifier). That needs power: usually phantom power, sometimes a battery or a dedicated supply for valve models.
- The diaphragm is very light, so condensers capture fast transients and high-frequency detail.
- Often higher output (for example 10–30 mV/Pa). A low-noise condenser can give a quieter recording of a quiet source, but compare the actual microphone and preamp specifications; the operating principle alone does not guarantee lower noise or lower maximum SPL.

### Ribbon

A very thin corrugated metal ribbon hangs in a magnetic field. Sound moves the ribbon, and induction generates a voltage, as in a dynamic mic. The ribbon has a tiny output and very low impedance, so passive ribbons use a step-up transformer.

- Open at front and back, a ribbon naturally has a **figure-8** pattern.
- Smooth, often darker high end.
- Physically fragile: a blast of air (wind, a kick drum port, blowing into it) can stretch the ribbon.

> [!warning] Ribbons and phantom power
> A correctly wired balanced cable puts phantom voltage equally on both signal pins, so an ideal floating passive output sees no differential DC. Damage can still happen with a faulty or miswired cable, with unbalanced adapters, or when hot-plugging with phantom on, because the pins don't make contact at the same instant. Switch phantom power **off** before connecting a passive ribbon (or anything that doesn't need it). Some modern "active" ribbons need phantom: follow the manufacturer's manual.

## Proximity effect

Directional (pressure-gradient) mics have a **bass boost when the source is very close**, within a few centimetres to tens of centimetres. Close to a small source, the pressure difference between the front and back of the diaphragm contains an extra component that is relatively strongest at low frequencies. The closer the source, the bigger the boost.

- Singers use it ("eating the mic" for a warm, big voice).
- It causes boomy, muddy recordings when you didn't want it.
- **Omnidirectional (pure pressure) mics have no proximity effect.**
- Many directional mics have a bass-cut switch to compensate.

## Key takeaways
- Moving-coil and ribbon microphones generate voltage by electromagnetic induction.
- Condenser microphones need power for their impedance-converting electronics.
- Pressure-gradient microphones can show proximity bass boost; pure pressure microphones do not.

## Further reading
- [Microphone technology — DPA](https://www.dpamicrophones.com/mic-university/technology/microphone-technology-the-essentials/)
- [U 87 Ai technical data — Neumann](https://www.neumann.com/en-en/products/microphones/u-87-ai/)
- [Phantom power — Schoeps](https://schoeps.de/en/knowledge/knowledge-base/technical-basics/phantom-power-p48p12.html)
- [Three-to-one rule — DPA](https://www.dpamicrophones.com/dict/3-1-rule/)
- [Ribbon microphone phantom precautions — Royer](https://royerlabs.com/faqs/)
