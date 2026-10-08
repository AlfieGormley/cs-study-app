---
id: midi-audio-levels
title: Audio levels and connections
level: intermediate
minutes: 17
summary: Mic, instrument, line, headphone and speaker levels and why they aren't interchangeable; −10 dBV versus +4 dBu with the voltage maths; balanced and unbalanced lines, TRS and TS, impedance bridging, DC offset and output coupling, and how to connect a DIY synth to an interface safely.
---

MIDI tells your synth what to play. This lesson is about the other cable: the **audio** that leaves your synth and goes into the audio interface. Getting it wrong gives you noise, hum, distortion, a quiet signal or, at worst, damaged equipment. Getting it right is mostly a matter of knowing the level conventions and a few circuit principles.

> [!warning] Safety boundaries
> Everything here concerns low-voltage signal connections. Don't open mains-powered gear, and never "fix" hum by removing a mains earth. Before connecting a home-built circuit to the interface, check the interface manual's maximum input level and connect with the gain turned down.

## The level hierarchy

Audio connections come in families with very different voltages and impedances:

| Level | Typical source | Goes into |
|---|---|---|
| Mic | Microphone | Mic preamp |
| Instrument | Guitar pickup | Hi-Z input |
| Line | Synth, mixer, DAC | Line input |
| Headphone | Headphone amp | Headphones |
| Speaker | Power amplifier | Passive speaker |

- **Mic level** is weak and varies widely between microphones (it is sometimes quoted as around −60 dBV). It needs a preamp with lots of gain.
- **Instrument level** comes from sources like guitar pickups that can supply very little current. "Hi-Z" instrument inputs present an input impedance of roughly 47 kΩ to over 1 MΩ so as not to load them.
- **Line level** is the level synths, mixers and interfaces use between each other. It is where your synth's output belongs.
- **Headphone outputs** are amplifiers designed to drive headphones with impedances from about 20 Ω to a few hundred ohms.
- **Speaker level** outputs from power amplifiers drive passive loudspeakers (usually 4–8 Ω) with much higher voltages and currents.

These are **not interchangeable**. A speaker output into a line input can overload or damage it. A line output into a speaker is nearly a short circuit for the line driver: very weak sound and a possibly damaged output. A headphone output can usually drive a line input (its source impedance is low), but it is designed for a different job and its level is set by a volume knob.

## Decibels with a reference: dBV and dBu

A decibel figure is a ratio. To describe an absolute voltage it needs a reference:

- **dBV**: relative to **1 V RMS**.
- **dBu**: relative to **0.7746 V RMS**, a holdover from 600 Ω telephone practice: the voltage that dissipates 1 mW in 600 Ω.

Where does 0.7746 V come from? Power in a resistor is voltage squared divided by resistance, so the voltage that gives a chosen power is the square root of power times resistance:

```formula
V_u = √(P × R)
V_u = √(0.001 W × 600 Ω)
V_u = √(0.6) V ≈ 0.7746 V
where
V_u: the dBu reference voltage (0 dBu), RMS, in volts (V)
P: the reference power, 1 milliwatt = 0.001 watts (W)
R: the reference load, 600 ohms (Ω), the old telephone-line standard
√: square root
W: watt, the unit of power
Ω: ohm, the unit of resistance
V: volt, the unit of voltage
≈: approximately equal to (rounded)
In words: 0.7746 V RMS is the voltage that would deliver one milliwatt into 600 ohms.
```

Today the 600 Ω load is history: 0 dBu just means 0.7746 V RMS, whatever the actual load.

To turn a level in decibels into a voltage, undo the decibel formula for voltage ratios (which uses 20 times the base-10 logarithm):

```formula
V_L = V_ref × 10^{L / 20}
V_L = 0.7746 V × 10^{4 / 20}
V_L = 0.7746 V × 1.585 ≈ 1.228 V
where
V_L: the RMS voltage the level L describes, in volts (V)
V_ref: the reference voltage: 0.7746 V for dBu, 1 V for dBV
L: the level in decibels relative to that reference (dBu or dBV); +4 here
10^{…}: 10 raised to the power in braces; it undoes a base-10 logarithm
V: volt, the unit of voltage
≈: approximately equal to (rounded)
In words: every 20 dB multiplies the voltage by 10, so +4 dB is about 1.585 times the reference, and +4 dBu is about 1.228 V RMS.
```

For −10 dBV the same formula, with a 1 V reference and a power of −10/20, gives about 0.316 V. The two nominal line levels:

- **Professional: +4 dBu.**
- **Consumer: −10 dBV.**

To compare two voltages in decibels, go the other way:

```formula
ΔL = 20 × log_10(V_1 / V_2)
ΔL = 20 × log_10(1.228 V / 0.316 V)
ΔL = 20 × log_10(3.88) ≈ 11.8 dB
where
ΔL: the difference in level, in decibels (dB); Δ (delta) means "difference"
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number; log_10(100) = 2
V_1: the larger voltage, RMS; 1.228 V (+4 dBu)
V_2: the smaller voltage, RMS; 0.316 V (−10 dBV)
V: volt
dB: decibel
≈: approximately equal to (rounded)
In words: pro line level is about 3.9 times the voltage of consumer line level, which is about 11.8 dB.
```

You can't just subtract −10 from +4 to get 14 dB, because the two figures use different references (0.7746 V and 1 V); converting both to volts first avoids that trap. The same sums in Python:

```python
import math

DBU_REF = math.sqrt(0.6)   # 0.7746 V
DBV_REF = 1.0

def dbu_to_v(dbu):
    return DBU_REF * 10 ** (dbu / 20)

def dbv_to_v(dbv):
    return DBV_REF * 10 ** (dbv / 20)

pro = dbu_to_v(4)
con = dbv_to_v(-10)
print(f"+4 dBu  = {pro:.3f} V rms")
print(f"-10 dBV = {con:.3f} V rms")
print(f"peak    = {pro*math.sqrt(2):.3f} V,"
      f" {con*math.sqrt(2):.3f} V")
print(f"gap     = "
      f"{20*math.log10(pro/con):.2f} dB")
```

```output
+4 dBu  = 1.228 V rms
-10 dBV = 0.316 V rms
peak    = 1.736 V, 0.447 V
gap     = 11.78 dB
```

So pro line level is about four times the voltage of consumer line level, about 12 dB higher. The "peak" line uses the relationship between a sine wave's RMS value and its peak:

```formula
V_peak = V_rms × √2
V_peak = 1.228 V × 1.414
V_peak ≈ 1.736 V
where
V_peak: the highest voltage the sine wave reaches, measured from 0 V, in volts (V)
V_rms: the RMS (root mean square) voltage, the "effective" value that level figures quote, in volts
√2: the square root of 2, about 1.414
V: volt
≈: approximately equal to (rounded)
In words: a sine wave's peaks are about 1.41 times its RMS value, so +4 dBu (1.228 V RMS) swings to about ±1.74 V.
```

The factor of about 1.414 holds only for a pure sine wave. Real music has a higher ratio of peak to RMS, which is one reason equipment needs headroom.

Two cautions:

- **Nominal is not maximum.** The nominal level is the design's operating level; real signals have peaks well above it, and equipment leaves **headroom** for them. Elektron, for example, specifies the Digitakt II's main outputs and inputs at +18 dBu peak, and the original Digitakt's main outputs at +22 dBu peak. Digital systems typically line nominal analogue level up with about −18 to −20 dBFS, leaving the rest for peaks.
- **Interfaces differ.** Many line inputs are switchable or have enough gain range to handle both conventions. Read your interface manual for its *maximum* input level (often in dBu) and compare it with your synth's maximum output.

## Impedance bridging

Audio line connections are not impedance-*matched* (that is for power transfer and radio). They use **impedance bridging**: a **low output impedance** drives a **high input impedance**. Wikipedia's line-level summary gives typical line outputs as 100–600 Ω and line inputs as 10 kΩ or more.

The output impedance and input impedance form a voltage divider: the source's voltage is shared between its own output impedance and the input impedance in proportion to their sizes, and only the input's share reaches the next stage.

```formula
V_in = V_src × Z_in / (Z_out + Z_in)
V_in = 1 V × 10000 Ω / (440 + 10000) Ω
V_in = 1 V × 0.958 ≈ 0.958 V
where
V_in: the voltage that actually arrives at the input, in volts (V)
V_src: the voltage the source generates internally, before its own output impedance, in volts
Z_in: the input impedance of the receiving device, in ohms (Ω); 10 kΩ here
Z_out: the output impedance of the source, in ohms; 440 Ω here (Elektron's figure for the Digitakt)
V: volt
Ω: ohm, the unit of resistance and impedance
≈: approximately equal to (rounded)
In words: the bigger the input impedance compared with the output impedance, the closer the received voltage is to the full source voltage.
```

In decibels a voltage ratio of 0.958 is about −0.4 dB, a negligible loss. The Digitakt's main outputs have a 440 Ω output impedance (Elektron's figure, unbalanced). See what happens to a 1 V signal from a 440 Ω source as the load changes:

```python
def bridged(v_src, z_out, z_in):
    # output and input form a divider
    return v_src * z_in / (z_out + z_in)

import math
for z_in in (10_000, 1_000, 32, 8):
    v = bridged(1.0, 440, z_in)
    db = 20 * math.log10(v)
    print(f"{z_in:>6} ohm: {v:.3f} V"
          f" ({db:.1f} dB)")
```

```output
 10000 ohm: 0.958 V (-0.4 dB)
  1000 ohm: 0.694 V (-3.2 dB)
    32 ohm: 0.068 V (-23.4 dB)
     8 ohm: 0.018 V (-35.0 dB)
```

Into a 10 kΩ line input, almost nothing is lost. Into a 32 Ω headphone or 8 Ω speaker, nearly all the voltage is dropped inside the source, and the output stage is asked for far more current than it was designed for. That is the numerical reason line, headphone and speaker connections are not interchangeable.

For your synth: give the output stage a **low output impedance** (an op-amp buffer or the codec's line driver), and expect to drive about 10 kΩ or more.

## Balanced and unbalanced connections

An **unbalanced connection** uses two conductors: signal and ground (which is also the shield). Any noise induced onto the signal wire, or any voltage difference between the two devices' grounds, adds directly to the audio.

A **balanced connection** (a **balanced line**) uses three: two signal conductors (hot and cold) with **equal impedances to ground**, plus a shield. Interference couples almost equally onto hot and cold, so it appears as a **common-mode** voltage. The receiver amplifies only the **difference** between hot and cold, which rejects the common-mode noise.

Notes that save confusion:

- Balancing is about **equal impedances**, not necessarily equal and opposite signals. An "impedance-balanced" output that drives only the hot leg, with the cold leg tied to ground through a matching impedance, still rejects common-mode noise. Elektron describes the Digitakt's main outputs as impedance balanced.
- Balanced connections usually use **XLR** or **1/4″ TRS**: tip = hot, ring = cold, sleeve = ground and shield.
- The same TRS plug is also used for **unbalanced stereo** (headphones: tip = left, ring = right). The connector alone doesn't tell you which; the jack's documentation does.
- **TS** (tip-sleeve) plugs are unbalanced mono.

Mixing them: a TS plug in a balanced output usually shorts the cold leg to ground. That is normal and fine for impedance-balanced outputs, but for some output designs the cold leg should be left disconnected instead, so check the manual. Feeding a balanced input from an unbalanced source works, but you lose most of the noise rejection.

> [!tip] For your first build
> An unbalanced mono output on a 1/4″ TS jack, buffered to a low output impedance, into a balanced line input on your interface, using a short cable, is a perfectly good start. Balanced output stages can come later if hum or noise demands it.

## DC offset and output coupling

Audio is an AC signal centred on 0 V. Many DIY synth circuits aren't:

- A microcontroller's built-in DAC on a single **3.3 V** supply outputs 0 V up to its reference voltage, so audio has to be centred on **mid-scale** (around 1.65 V) and swing either side of that.
- Many single-supply audio codecs likewise bias their analogue outputs to an internal **mid-supply** reference. Not all do: TI's PCM510x DACs, for example, use an internal charge pump to give ground-centred outputs that need no DC-blocking capacitor. Check your part's datasheet.
- An op-amp stage on a single supply has the same issue.

That constant offset is **DC**. Sent into an interface, it can shift the input stage's operating point, eat headroom, cause thumps when plugging and unplugging, and push speaker cones off centre. So the output is normally **AC-coupled**: a series **coupling capacitor** passes the audio and blocks the DC.

The capacitor and the next stage's input impedance form a **high-pass filter**. Its corner frequency, below which the bass starts to roll off, is:

```formula
f_c = 1 / (2 × π × R_in × C)
f_c = 1 / (2 × π × 10000 Ω × 0.00001 F)
f_c = 1 / 0.628 s ≈ 1.59 Hz
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

def hp_corner(c_farads, r_ohms):
    return 1 / (2 * math.pi * r_ohms
                * c_farads)

print(round(hp_corner(10e-6, 10_000), 2))
print(round(hp_corner(1e-6, 10_000), 2))
print(round(hp_corner(10e-6, 21_000), 2))
```

```
1.59
15.92
0.76
```

- 10 µF into a 10 kΩ input: corner about 1.6 Hz, well below the 20 Hz bottom of hearing.
- 1 µF into 10 kΩ: about 16 Hz, which already starts to thin the lowest bass, especially as cascaded coupling stages add up.
- 10 µF into the Digitakt II's 21 kΩ inputs: about 0.8 Hz.

Choose C so that the corner sits comfortably below 20 Hz for the *lowest* input impedance you expect to drive. Use a capacitor type with a low voltage coefficient, and if it is a polarised electrolytic, orient it for the DC across it (positive towards the biased circuit side).

> [!note] Check what your board already does
> Some audio codec boards already AC-couple and buffer their line outputs; others expose a raw DAC pin. Don't assume. Read the board's datasheet or schematic for the output's DC bias, maximum swing and output impedance before adding (or omitting) a coupling capacitor and buffer.

### A worked level check

Suppose (hypothetically) your synth's output stage swings a full-scale sine between 0 V and 3.3 V, centred on 1.65 V. After AC coupling, that is a 1.65 V peak sine. Convert the peak to RMS, then express the RMS voltage relative to the dBu reference:

```formula
V_rms = V_peak / √2
V_rms = 1.65 V / 1.414 ≈ 1.167 V
L = 20 × log_10(V_rms / 0.7746 V)
L = 20 × log_10(1.167 V / 0.7746 V)
L = 20 × log_10(1.506) ≈ +3.56 dBu
where
V_rms: the RMS (root mean square) voltage of the sine, in volts (V)
V_peak: the sine's peak voltage after the DC is removed; half of the 3.3 V swing, 1.65 V
√2: the square root of 2, about 1.414
L: the output level in dBu (decibels relative to 0.7746 V RMS)
log_10: the base-10 logarithm, the power of 10 that gives the number
0.7746 V: the dBu reference voltage
V: volt
dBu: decibels relative to 0.7746 V RMS
≈: approximately equal to (rounded)
In words: a 1.65 V-peak sine is about 1.17 V RMS, which is about 3.6 dB above the 0.7746 V dBu reference.
```

That's close to pro nominal level at full scale, and well within a line input that accepts, say, +18 dBu. You'd set the interface gain low, and there's no risk of overload. If instead your output were much smaller, you would add gain at the synth's output stage rather than crank the interface preamp and amplify its noise.

## Connecting your synth to the interface safely

A checklist for the first connection:

1. **Read both manuals.** Note the synth's maximum output level and DC behaviour, and the interface's input types, impedances and maximum levels.
2. **Use a line input** (or a combo jack's 1/4″ line path), not the speaker terminals of anything, and not a mic input with phantom power.
3. **Turn off 48 V phantom power** on that channel. Phantom power is intended for microphones; with some cables, adapters and electronic instruments it can cause malfunction or even damage.
4. **Gain to minimum, monitors down**, then connect, then power up the synth.
5. **Measure first.** With an oscilloscope or multimeter, confirm the output has no significant DC offset and that its swing is what you expect.
6. **Bring the gain up** until peaks sit comfortably below clipping on the interface meter (lesson 6 covers gain staging).
7. **Protect the output.** A small series resistor at the synth's output and a buffered stage keep a shorted cable or a mis-plugged headphone load from damaging your circuit. Follow your board vendor's recommended output circuit.

## Key takeaways
- Mic, instrument, line, headphone and speaker levels differ in voltage and impedance, and are not interchangeable. A synth output belongs in a line input.
- +4 dBu = 1.228 V RMS (pro); −10 dBV = 0.316 V RMS (consumer); the gap is about 11.8 dB. Nominal isn't maximum: check each device's maximum level.
- Line connections bridge a low output impedance (100–600 Ω) into a high input impedance (≥10 kΩ); driving low-impedance loads collapses the voltage and strains the output.
- Balanced lines reject common-mode noise through equal impedances and a differential receiver; TRS can mean balanced mono or unbalanced stereo, so check the jack's documentation.
- Single-supply DIY outputs carry DC offset; AC-couple them with a capacitor sized so the high-pass corner it forms with the input resistance is well below 20 Hz, and connect with phantom power off and gain down.

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
