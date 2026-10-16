---
id: midi-audio-levels-voltage-references
title: Convert between line levels and volts
level: intermediate
minutes: 4
sourceLesson: midi-audio-levels
summary: Compare dBu and dBV through their level reference voltages; their displayed numbers cannot be subtracted directly.
---

## Decibels with a reference: dBV and dBu

A decibel figure is a ratio. To describe an absolute voltage it needs a reference:

- **dBV**: relative to **1 V RMS**.
- **dBu**: relative to **0.7746 V RMS**, a holdover from 600 Ω telephone practice: the voltage that dissipates 1 mW in 600 Ω.

Where does 0.7746 V come from? Power in a resistor is voltage squared divided by resistance, so the voltage that gives a chosen power is the square root of power times resistance:

```formula
V_u = √(PR)
V_u = √(0.001 W × 600 Ω)
V_u = √(0.6) V ≈ 0.7746 V
where
V_u: the dBu level reference voltage (0 dBu), RMS, in volts (V)
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
V_L = V_ref 10^{L / 20}
V_L = 0.7746 V × 10^{4 / 20}
V_L = 0.7746 V × 1.585 ≈ 1.228 V
where
V_L: the RMS voltage the level L describes, in volts (V)
V_ref: the level reference voltage: 0.7746 V for dBu, 1 V for dBV
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
ΔL = 20 log_10(V_1 / V_2)
ΔL = 20 log_10(1.228 V / 0.316 V)
ΔL = 20 log_10(3.88) ≈ 11.8 dB
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

# Historical reference: 1 mW into 600 ohms.
DBU_REF = math.sqrt(0.6)   # 0.7746 V
DBV_REF = 1.0

def dbu_to_v(dbu):
    return DBU_REF * 10 ** (dbu / 20)

def dbv_to_v(dbv):
    return DBV_REF * 10 ** (dbv / 20)

# Voltages are RMS; peak below assumes a
# sine.
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

For a pure sine, peak voltage is about 1.414 times RMS voltage; that relationship explains the peak output line above. The following headroom unit explains why it does not hold for an arbitrary waveform.

## Key takeaways
- Compare dBu and dBV through their level reference voltages; their displayed numbers cannot be subtracted directly.

## Further reading
- [Signal processing fundamentals and level references — Rane](https://www.ranecommercial.com/legacy/pdf/ranenotes/Signal_Processing_Fundamentals.pdf)
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
