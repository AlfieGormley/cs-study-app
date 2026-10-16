---
id: aud-amplifiers-voltage-and-power
title: Voltage gain, current and load power
level: advanced
minutes: 4
summary: An amplifier supplies output voltage and the current required by its load within its limits.
sourceLesson: aud-amplifiers
---

Your synth's line output can swing a volt or two into 10 kΩ or more (module 5). A loudspeaker needs tens of volts into a few ohms: amps of current and tens or hundreds of watts. A **power amplifier** bridges that gap.

> [!warning] Safety: conceptual lesson only
> Power amplifiers contain **mains wiring** and, inside, **high-voltage supply rails and large capacitors** that can stay charged after unplugging. Valve (tube) amps run at hundreds of volts. Speaker terminals on a large amp can carry voltages that are dangerous to touch at full power. This lesson is about understanding and choosing amplifiers. **Don't open, modify or build mains-powered amplifiers.** Connect speakers with the amp switched off and the volume down, and leave repairs to qualified technicians.

## What a power amp does

A power amp is a **voltage amplifier with a very low output impedance** that can deliver large currents:

- It multiplies the input voltage by a fixed **voltage gain**.
- It holds that output voltage steady whatever the speaker's impedance does (within its limits), by supplying whatever current the load demands.
- Power is a *result*. The amp sets the voltage; the speaker's impedance decides the current and so the power.

For a resistive load, Ohm's law and the power formula tell you the current and power from the voltage:

```formula
I_rms = V_rms / R
P = V_rms^2 / R
I_rms = 20 V / 8 Ω = 2.5 A
P = (20 V)^2 / 8 Ω = 400 / 8 = 50 W
where
I_rms: the RMS current through the speaker, in amperes (A)
V_rms: the RMS (root-mean-square, an "effective average") output voltage, in volts (V)
R: the load resistance, in ohms (Ω); a nominal speaker is typically 4 Ω or 8 Ω
P: the average power delivered to the load, in watts (W)
A: amperes (amps), the unit of current
V: volts, the unit of voltage
Ω: ohms, the unit of resistance
W: watts, the unit of power
In words: power rises with the square of voltage, so doubling the voltage gives four times the power, and halving the resistance doubles it.
```

That's exact only for a resistor. A real speaker has complex impedance, so sinusoidal real power also depends on the voltage–current phase difference.

### Voltage gain vs power

Amplifier gain is usually quoted in dB (voltage), or as **input sensitivity**: the input voltage that produces full rated output. To use a dB gain, turn it back into a multiplier:

```formula
G = 10^{G_dB / 20}
G = 10^{26 / 20} ≈ 19.95
V_in = 0.7746 V × 10^{4 / 20} ≈ 1.228 V
V_out = V_in G
V_out = 1.228 V × 19.95 ≈ 24.5 V
P = (24.5 V)^2 / 8 Ω ≈ 75 W
V_sens = √(P_max R) / G
V_sens = √(100 W × 8 Ω) / 19.95 ≈ 1.42 V
where
G: the voltage gain as a plain multiplier (no unit)
G_dB: the voltage gain in decibels (dB), here 26 dB
V_in: the RMS input voltage, in volts (V); +4 dBu (professional line level) is 0.7746 V × 10^(4/20) ≈ 1.228 V
V_out: the RMS output voltage, in volts (V)
P: the average power into the load, in watts (W)
R: the load resistance, 8 ohms (Ω)
V_sens: the input sensitivity: the input voltage that gives the rated maximum power, in volts (V)
P_max: the rated maximum power, here 100 W
√: square root
≈: approximately equal to
V: volts
W: watts
Ω: ohms
dB: decibel; dividing by 20 converts a voltage decibel figure back to a ratio
In words: 26 dB is a voltage gain of about 20, so a +4 dBu line signal comes out at about 24.5 V, which is 75 W into 8 Ω; you'd need about 1.42 V in to reach 100 W.
```

So an amp with 26 dB gain fed a +4 dBu signal gives about 24.5 V RMS: 75 W into 8 Ω. Gain and maximum output power are separate specifications. Higher power may require greater voltage swing, greater current capacity or both; different models may also have different gain. (26 dB is used here as an illustration: real amps range widely, and many quote sensitivity instead. Read the manual.)

## Key takeaways
- An amplifier supplies output voltage and the current required by its load within its limits.
- Gain and maximum clean output are different specifications.
- The simple voltage-squared power calculation assumes a resistive load.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
