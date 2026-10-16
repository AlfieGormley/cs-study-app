---
id: midi-audio-levels-balanced-connectors
title: Read balanced and stereo jack wiring
level: intermediate
minutes: 3
sourceLesson: midi-audio-levels
summary: A balanced line relies on impedance symmetry and a differential receiver; a TRS connector alone proves neither balance nor signal type.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Balanced and unbalanced connections

An **unbalanced connection** uses two conductors: signal and ground (which is also the shield). Any noise induced onto the signal wire, or any voltage difference between the two devices' grounds, adds directly to the audio.

A **balanced connection** (a **balanced line**) uses three: two signal conductors (hot and cold) with **equal impedances to ground**, plus a shield. Interference couples almost equally onto hot and cold, so much of it appears as a **common-mode** voltage. A differential receiver responds primarily to the **difference** between the conductors. Rejection is finite and depends on impedance balance, cable construction and the receiver.

Notes that save confusion:

- Balancing is about **equal impedances**, not necessarily equal and opposite signals. An "impedance-balanced" output that drives only the hot leg, with the cold leg tied to ground through a matching impedance, can still provide common-mode rejection with a suitable balanced receiver. Elektron describes the Digitakt's main outputs as impedance balanced.
- Balanced connections usually use **XLR** or **1/4″ TRS**: tip = hot, ring = cold, sleeve = ground and shield.
- The same TRS plug is also used for **unbalanced stereo** (headphones: tip = left, ring = right). The connector alone doesn't tell you which; the jack's documentation does.
- **TS** (tip-sleeve) plugs are unbalanced mono.

Mixing them: a TS plug in a balanced output usually shorts the cold leg to ground. That is normal and fine for impedance-balanced outputs, but for some output designs the cold leg should be left disconnected instead, so check the manual. An unbalanced source can feed a balanced input using the manufacturer's recommended wiring. Noise rejection depends on the resulting impedances and connections; do not assume a particular amount of rejection survives or is lost.

> [!tip] For your first build
> An unbalanced mono output on a 1/4″ TS jack, buffered to a low output impedance, into a balanced line input on your interface, using a short cable, is a perfectly good start. Balanced output stages can come later if hum or noise demands it.

## Key takeaways
- A balanced line relies on impedance symmetry and a differential receiver; a TRS connector alone proves neither balance nor signal type.

## Further reading
- [Sound system interconnection — Rane](https://www.ranecommercial.com/legacy/note110.html)
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Nominal level — Wikipedia](https://en.wikipedia.org/wiki/Nominal_level)
- [Impedance bridging — Wikipedia](https://en.wikipedia.org/wiki/Impedance_bridging)
- [Balanced audio — Wikipedia](https://en.wikipedia.org/wiki/Balanced_audio)
- [Capacitive coupling (coupling capacitors and their high-pass effect) — Wikipedia](https://en.wikipedia.org/wiki/Capacitive_coupling)
- [Phantom power — Wikipedia](https://en.wikipedia.org/wiki/Phantom_power)
- [Single-supply biasing (op amps biased at half supply, coupling capacitors) — LibreTexts, from J. Fiore's op amp textbook](https://eng.libretexts.org/Workbench/Introduction_to_Circuit_Analysis/05%3A_Advanced_Topic-_Operational_Amplifiers/5.10%3A_Basic_Op_Amp_Circuits/5.10.03%3A_Single_Supply_Biasing)
- [Single-Supply Op Amp Design Techniques (SLOA030) — Texas Instruments](https://www.ti.com/lit/an/sloa030a/sloa030a.pdf)
- [PCM5102A data sheet (ground-centred 2.1 V RMS output) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
- [Digitakt II user manual, technical information — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Balanced and unbalanced equipment — Jensen AN-003](https://www.jensen-transformers.com/wp-content/uploads/2014/08/an003.pdf)
