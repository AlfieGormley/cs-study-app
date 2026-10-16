---
id: elec-audio-hum-budget
sourceLesson: elec-noise-grounding
title: "Calculating an audio hum budget"
level: advanced
minutes: 3
summary: "Small return-wire voltages can matter after amplification."
---

A synth that works can still be unusable if it hums, buzzes or whines. Noise can come from components, interference, supply coupling and **how currents return**. These units focus on wiring, grounding and power coupling. This lesson gives you the mental model to diagnose noise in your own studio: a synth board, a Digitakt, an audio interface and a computer running Ableton.

> [!warning] Never touch the safety earth
> Some "fixes" for hum online involve removing or cutting the earth connection of mains equipment ("ground lifting" the plug). **Never do this.** The protective earth is what makes a fault safe. Rane's grounding note says: "Safety regulations require that all original grounding means provided from the factory be left intact for safe operation." Everything in this lesson works at the signal level or uses equipment designed for isolation.

## Why audio is so sensitive
Digital links have specified threshold margins, sometimes only a few tenths of a volt. Audio has no digital-style logic threshold: added noise can be amplified, but whether it is audible depends on gain, spectrum, masking and the listening system. A commonly used consumer nominal line reference is −10 dBV; actual device outputs and input headroom vary, so read the exact manuals. Converting that level to volts:

```formula
V = 1 V × 10^{L/20}
V = 1 V × 10^{−10/20} ≈ 0.316 V
where
V: the signal's RMS voltage, in volts (V)
L: the level in dBV, decibels relative to 1 volt RMS; here −10 dBV
10^{L/20}: ten raised to the power L ÷ 20, which turns decibels back into a voltage ratio
dBV: decibels relative to 1 V RMS
≈: approximately equal to (rounded)
In words: −10 dBV is about 0.316 volts RMS, roughly a third of a volt.
```

A clean system's noise sits tens of decibels below that, so a few hundred microvolts of hum can be clearly audible. To see how far below the signal some hum sits, find the hum voltage with Ohm's law, then express the ratio in decibels:

```formula
V_hum = I_loop R_shield
V_hum = 0.001 A × 0.1 Ω = 0.0001 V
L_SH = 20 log_10(V_sig / V_hum)
L_SH = 20 log_10(0.316 V / 0.0001 V)
L_SH ≈ 20 × 3.5 = 70 dB
where
V_hum: the hum RMS voltage added to the signal, in volts (V); 0.0001 V is 100 µV
I_loop: the RMS unwanted current flowing in the cable shield, here 1 mA = 0.001 amperes (A)
R_shield: the shield's resistance, here 100 mΩ = 0.1 ohms (Ω)
L_SH: the signal-to-hum ratio, in decibels (dB)
V_sig: the signal voltage, here 0.316 V RMS
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number (log_10(1000) = 3)
V: volts
A: amperes
Ω: ohms
dB: decibels; 20 dB is a factor of 10 in voltage
≈: approximately equal to (rounded)
In words: 1 mA through a 0.1 Ω shield makes 100 µV of hum, which sits about 70 dB below a −10 dBV signal.
```

The same sums in Python:

```python
import math

def db(ratio):
    return 20 * math.log10(ratio)

i_loop = 0.001    # 1 mA of 50 Hz current
r_shield = 0.1    # 100 mΩ cable shield
# Illustrative RMS drop across the shield.
v_hum = i_loop * r_shield

v_sig = 10 ** (-10 / 20)  # -10 dBV line
print(f"hum: {v_hum * 1e6:.0f} uV")
print(f"signal: {v_sig:.3f} V")
print(f"S/hum: {db(v_sig / v_hum):.1f} dB")
```

```
hum: 100 uV
signal: 0.316 V
S/hum: 70.0 dB
```

The 1 mA and 100 mΩ figures are illustrative, not measured; real loop currents and shield resistances vary widely. The mechanism (loop current × shield resistance adds to the signal) is the one Wikipedia's ground-loop article derives. Hum only 70 dB below the signal may be heard in quiet passages or with gain applied afterwards.

## Key takeaways

- Small return-wire voltages can matter after amplification.
- State whether voltages are RMS before using a decibel ratio.

## Further reading

- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
- [Analog Devices MT-031: converter grounding](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)
