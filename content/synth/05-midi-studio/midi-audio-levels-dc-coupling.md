---
id: midi-audio-levels-dc-coupling
title: Block DC without losing low bass
level: intermediate
minutes: 4
sourceLesson: midi-audio-levels
summary: Check actual board bias and coupling, then size the capacitor for the lowest input impedance and its tolerance.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## DC offset and output coupling

For the external analogue line connection here, the wanted changing audio signal should have little unintended DC offset. Many DIY synth circuits aren't:

- An MCU DAC limited to non-negative voltages may have a nominal range from zero towards its positive reference (check actual swing and load limits), so a bipolar waveform can be biased near **mid-scale** (1.65 V in an ideal 3.3 V range) and swing either side of that.
- Many single-supply audio codecs likewise bias their analogue outputs to an internal **mid-supply** reference. Not all do: TI's PCM510x DACs, for example, use an internal charge pump to give ground-centred outputs that need no DC-blocking capacitor. Check your part's datasheet.
- A single-supply op-amp stage commonly needs bias and coupling too; suitable charge-pump or other circuitry can provide ground-centred outputs.

That constant offset is **DC**. Sent into an interface, it can shift the input stage's operating point, eat headroom, cause thumps when plugging and unplugging, and push speaker cones off centre. So the output is normally **AC-coupled**: a series **coupling capacitor** passes the audio and blocks the DC.

The capacitor and the next stage's input impedance form a **high-pass filter**. Its corner frequency, below which the bass starts to roll off, is:

```formula
f_c = 1 / (2πR_in C)
f_c = 1 / (2 × π × 10000 Ω × 0.00001 F)
f_c = 1 / (0.628 s) ≈ 1.59 Hz
where
f_c: the corner (cut-off) frequency, in hertz (Hz): the frequency where the output has fallen to about 71% of the input (−3 dB); below it the response falls by about 6 dB per octave
π: pi, about 3.14159
R_in: the input resistance of the next stage, in ohms (Ω); 10 kΩ here
C: the coupling capacitance, in farads (F); 10 µF = 0.00001 F here
Ω: ohm, the unit of resistance
F: farad, the unit of capacitance (ohms times farads gives seconds)
s: seconds
Hz: hertz, cycles per second
≈: approximately equal to (rounded)
In words: the bigger the capacitor or the input resistance, the lower the corner; 10 µF into 10 kΩ only starts cutting at about 1.6 Hz, far below anything audible.
```

This approximation assumes the source's output resistance is much smaller than the input resistance. If it isn't, use the source's output resistance plus the input resistance in place of the input resistance. The same calculation in Python, for three cases:

```python
import math

# Ideal capacitor; source resistance
# neglected.
def hp_corner(c_farads, r_ohms):
    return 1 / (2 * math.pi * r_ohms
                * c_farads)

# Output is the corner frequency in hertz.
print(round(hp_corner(10e-6, 10_000), 2))
print(round(hp_corner(1e-6, 10_000), 2))
print(round(hp_corner(10e-6, 21_000), 2))
```

```output
1.59
15.92
0.76
```

- 10 µF into a 10 kΩ input: corner about 1.6 Hz, well below the 20 Hz bottom of hearing.
- 1 µF into 10 kΩ: about 16 Hz, which already starts to thin the lowest bass, especially as cascaded coupling stages add up.
- 10 µF into the Digitakt II's 21 kΩ inputs: about 0.8 Hz.

Choose C so that the corner sits comfortably below 20 Hz for the *lowest* input impedance you expect to drive. Account for capacitor tolerance, voltage rating and voltage coefficient, and if it is a polarised electrolytic, orient it for the DC across it (positive towards the side at the higher DC potential; check both ends under normal and transient conditions).

> [!note] Check what your board already does
> Some audio codec boards already AC-couple and buffer their line outputs; others expose a raw DAC pin. Don't assume. Read the board's datasheet or schematic for the output's DC bias, maximum swing and output impedance before adding (or omitting) a coupling capacitor and buffer.

## Key takeaways
- Check actual board bias and coupling, then size the capacitor for the lowest input impedance and its tolerance.

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
