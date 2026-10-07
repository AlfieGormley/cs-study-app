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
- **Speaker outputs** from power amplifiers drive passive loudspeakers (usually 4–8 Ω) with much higher voltages and currents.

These are **not interchangeable**. A speaker output into a line input can overload or damage it. A line output into a speaker is nearly a short circuit for the line driver: very weak sound and a possibly damaged output. A headphone output can usually drive a line input (its source impedance is low), but it is designed for a different job and its level is set by a volume knob.

## Decibels with a reference: dBV and dBu

A decibel figure is a ratio. To describe an absolute voltage it needs a reference:

- **dBV**: relative to **1 V RMS**.
- **dBu**: relative to **0.7746 V RMS** (√0.6 V), a holdover from 600 Ω telephone practice: the voltage that dissipates 1 mW in 600 Ω.

Voltage in decibels uses 20·log10, so V = V_ref × 10^(dB/20). The two nominal line levels:

- **Professional: +4 dBu.**
- **Consumer: −10 dBV.**

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

```
+4 dBu  = 1.228 V rms
-10 dBV = 0.316 V rms
peak    = 1.736 V, 0.447 V
gap     = 11.78 dB
```

So pro line level is about four times the voltage of consumer line level, about 12 dB higher. For a sine wave, peak = RMS × √2 (the "peak" line above).

Two cautions:

- **Nominal is not maximum.** The nominal level is the design's operating level; real signals have peaks well above it, and equipment leaves **headroom** for them. Elektron, for example, specifies the Digitakt II's main outputs and inputs at +18 dBu peak, and the original Digitakt's main outputs at +22 dBu peak. Digital systems typically line nominal analogue level up with about −18 to −20 dBFS, leaving the rest for peaks.
- **Interfaces differ.** Many line inputs are switchable or have enough gain range to handle both conventions. Read your interface manual for its *maximum* input level (often in dBu) and compare it with your synth's maximum output.

## Impedance bridging

Audio line connections are not impedance-*matched* (that is for power transfer and radio). They are **bridged**: a **low output impedance** drives a **high input impedance**. Wikipedia's line-level summary gives typical line outputs as 100–600 Ω and line inputs as 10 kΩ or more.

The output impedance and input impedance form a voltage divider:

```
V_in = V_src * Z_in / (Z_out + Z_in)
```

The Digitakt's main outputs have a 440 Ω output impedance (Elektron's figure, unbalanced). See what happens to a 1 V signal from a 440 Ω source as the load changes:

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

```
 10000 ohm: 0.958 V (-0.4 dB)
  1000 ohm: 0.694 V (-3.2 dB)
    32 ohm: 0.068 V (-23.4 dB)
     8 ohm: 0.018 V (-35.0 dB)
```

Into a 10 kΩ line input, almost nothing is lost. Into a 32 Ω headphone or 8 Ω speaker, nearly all the voltage is dropped inside the source, and the output stage is asked for far more current than it was designed for. That is the numerical reason line, headphone and speaker connections are not interchangeable.

For your synth: give the output stage a **low output impedance** (an op-amp buffer or the codec's line driver), and expect to drive about 10 kΩ or more.

## Balanced and unbalanced connections

An **unbalanced** connection uses two conductors: signal and ground (which is also the shield). Any noise induced onto the signal wire, or any voltage difference between the two devices' grounds, adds directly to the audio.

A **balanced** connection uses three: two signal conductors (hot and cold) with **equal impedances to ground**, plus a shield. Interference couples almost equally onto hot and cold, so it appears as a **common-mode** voltage. The receiver amplifies only the **difference** between hot and cold, which rejects the common-mode noise.

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

The capacitor and the next stage's input impedance form a **high-pass filter**. This approximation assumes source output resistance is much smaller than `R_in`; otherwise use `R_out + R_in` for the resistance:

```
f_c = 1 / (2 * pi * R_in * C)
```

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

Suppose (hypothetically) your synth's output stage swings a full-scale sine between 0 V and 3.3 V, centred on 1.65 V. After AC coupling, that is a 1.65 V peak sine:

```
V_rms = 1.65 / sqrt(2)     = 1.167 V
dBu   = 20*log10(1.167/0.7746)
      = +3.56 dBu
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
- Single-supply DIY outputs carry DC offset; AC-couple them with a capacitor sized so 1/(2πRC) is well below 20 Hz, and connect with phantom power off and gain down.

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
