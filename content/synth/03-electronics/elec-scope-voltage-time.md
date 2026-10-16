---
id: elec-scope-voltage-time
sourceLesson: elec-measurement-soldering
title: "What an oscilloscope shows and its ground clip"
level: intermediate
minutes: 2
summary: "A scope shows waveform shape and timing, within its limits."
---

A scope shows waveform shape and timing, within its limits.

## The oscilloscope: seeing voltage over time
A multimeter gives one number: a DC value or an AC summary whose meaning depends on the meter and waveform. An **oscilloscope** draws voltage against time, so you can see what's actually happening:

- the shape of an audio waveform, and whether it clips;
- noise and supply ripple riding on a rail;
- logic or PWM signals and their timing;
- switch bounce lasting a few milliseconds.

Core controls:

- **Vertical (V/div):** volts per grid square.
- **Horizontal (time/div):** seconds per grid square.
- **Trigger** (the oscilloscope trigger): the condition (a level and a rising or falling edge) that starts each sweep at the same point, so a repeating waveform stands still on screen.
- **Probe ×1/×10:** ×10 probes load the circuit less and extend bandwidth. Set the scope to match the probe.

> [!warning] Probe ground clips
> On a typical mains-powered bench scope, the probe's ground clip is connected to protective earth through the scope. In this low-voltage project, connect it only to the documented ground reference after checking the instrument and circuit grounding. Multiple ordinary channel ground clips are normally connected together. Connecting it to another point in a circuit that's also earth-referenced creates a short through the probe. A circuit is earth-referenced if anything connected to it ties its ground to earth: a desktop PC's USB port usually does, and so do some laptop adapters with three-pin plugs, while two-pin laptop adapters usually leave the output floating. Don't rely on knowing which. To measure across a component, use two correctly configured probes (both grounds on circuit ground) and the scope’s A − B maths, or a suitable differential probe. Keep each probe’s voltage, common-mode, bandwidth and instrument ratings within its specified limits; subtraction does not isolate an ordinary probe. Never defeat a scope's safety earth to "float" it. Instrument manuals strongly warn against it.

The project doesn't require owning a scope at first. A multimeter covers the foundation exercises. Consider a scope when you need to debug noise, audio clipping or timing that a meter can't show.

## Key takeaways

- A scope shows waveform shape and timing, within its limits.
- Keep ordinary probe ground clips on the documented circuit ground.

## Further reading

- [Tektronix: floating measurements and grounding](https://www.tek.com/en/documents/technical-brief/floating-oscilloscope-measurements-and-operator-protection)
