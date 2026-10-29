---
id: midi-audio-levels-first-interface-check
title: Measure before the first audio connection
level: intermediate
minutes: 3
sourceLesson: midi-audio-levels
summary: Verify DC and waveform swing with appropriate instruments, then connect a documented line path with phantom power off and levels down.
---

## A worked level check

Before connecting anything, estimate where your output sits. Suppose (hypothetically) your synth's output stage swings a full-scale sine between 0 V and 3.3 V, centred on 1.65 V. Reason it through in steps:

1. **Remove the DC.** After AC coupling, the sine swings 1.65 V either side of zero: a 1.65 V *peak*.
2. **Convert peak to RMS.** For a sine, divide the peak by about 1.414: about 1.17 V RMS.
3. **Compare with the line levels.** That is a little below the professional +4 dBu nominal level (about 1.23 V RMS), roughly +3.6 dBu.

The common mistakes are treating 3.3 V or 1.65 V as an RMS value, which overstates the level by several decibels.

So the output is close to pro nominal level at full scale, and well within a line input that accepts, say, +18 dBu. Still set the interface gain low and verify the actual peak voltage and transients: the ideal sine calculation alone does not prove the hardware cannot overload. For a smaller output, compare the clean gain available in the synth and the interface; the noise outcome depends on both stages, and extra output gain is not automatically quieter.

## Connecting your synth to the interface safely

A checklist for the first connection:

1. **Read both manuals.** Note the synth's maximum output level and DC behaviour, and the interface's input types, impedances and maximum levels.
2. **Use a line input** (or a combo jack's 1/4″ line path), not the speaker terminals of anything, and not a mic input with phantom power.
3. **Turn off 48 V phantom power** on that channel. Phantom power is intended for microphones; with some cables, adapters and electronic instruments it can cause malfunction or even damage.
4. **Measure before connecting to the interface.** Power the isolated low-voltage synth as documented. Use a DC-voltage meter to check offset, and an oscilloscope (or a suitably rated, frequency-specified AC meter) to check waveform swing. An ordinary meter alone cannot reveal short peaks or clipping.
5. **Gain to minimum, monitors down.** After the output checks, connect following both devices’ documented power-up and connection procedure.
6. **Bring the gain up** until peaks sit comfortably below clipping on the interface meter (**Leave headroom at every stage** covers this).
7. **Protect the output.** A suitable buffer and documented series resistance can improve fault tolerance, but do not guarantee survival of every short or load. Follow your board vendor's recommended output circuit.

## Key takeaways
- Estimate the level first: a 0–3.3 V full-scale sine, once AC-coupled, is about 1.17 V RMS, close to +4 dBu nominal.
- Measure DC offset and waveform swing with suitable instruments before connecting.
- Connect to a line input with phantom power off, gain at minimum and monitors down, then raise the gain gradually.

## Further reading
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
