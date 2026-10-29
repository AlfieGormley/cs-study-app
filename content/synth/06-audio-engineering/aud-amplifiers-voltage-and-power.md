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
> Power amplifiers contain **mains wiring** and, inside, **high-voltage supply rails and large capacitors** that can stay charged after unplugging. Valve (tube) amplifiers run at hundreds of volts. Speaker terminals on a large amp can carry voltages that are dangerous to touch at full power. This lesson is about understanding and choosing amplifiers. **Don't open, modify or build mains-powered amplifiers.** Connect speakers with the amp switched off and the volume down, and leave repairs to qualified technicians.

## What a power amp does

A power amp is a **voltage amplifier with a very low output impedance** that can deliver large currents:

- It multiplies the input voltage by a fixed **voltage gain**.
- It holds that output voltage steady whatever the speaker's impedance does (within its limits), by supplying whatever current the load demands.
- Power is a *result*. The amp sets the voltage; the speaker's impedance decides the current and so the power.

For a resistive load, Ohm's law gives the current from the voltage, and the power follows:

```formula essential
I_rms = V_rms / R
P = V_rms^2 / R
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

For example, 20 V RMS across 8 Ω pushes 2.5 A and delivers 50 W. The same 20 V across 4 Ω pushes 5 A and delivers 100 W, provided the amplifier can supply that current. That's exact only for a resistor. A real speaker has complex impedance, so sinusoidal real power also depends on the voltage–current phase difference.

> [!analogy] Real-world analogy: a water main and a tap
> The water main holds its pressure steady. Open a narrow tap and a little water flows; open a wide one and much more flows, from the same pressure. How much water you get, and how hard the main has to work, depends on the tap, not just the main.
>
> **How it maps:** The amplifier is the main holding a steady voltage (pressure). The speaker's impedance is the tap's narrowness: a lower impedance is a wider tap that draws more current (flow). Power is pressure times flow, so a 4 Ω speaker draws more power than an 8 Ω one at the same voltage.
>
> **Where it stops:** A speaker's impedance changes with frequency and stores and returns energy, so current and voltage do not stay in step the way water flow and pressure do through a simple tap. And a real amplifier's "main" has a hard limit on how much current it can supply.

### Voltage gain vs power

Amplifier gain is usually quoted in dB (voltage), or as **input sensitivity**: the input voltage that produces full rated output. Gain in voltage decibels converts back to a multiplier exactly as in module 1: 6 dB is about ×2, 20 dB is ×10, and 26 dB is about ×20.

So an amplifier with 26 dB of gain fed a +4 dBu line signal (about 1.23 V RMS) puts out about 24.5 V RMS: about 75 W into 8 Ω. To reach a 100 W rating into 8 Ω it would need about 1.4 V in; that figure is its input sensitivity.

The key point is that **gain and maximum output power are separate specifications**. Below clipping, two amplifiers with the same gain play the same signal at the same level, whatever their power ratings; the bigger one simply has more headroom before it clips. Higher power may require greater voltage swing, greater current capacity or both; different models may also have different gain. (26 dB is used here as an illustration: real amplifiers range widely, and many quote sensitivity instead. Read the manual.)

## Key takeaways
- An amplifier supplies output voltage and the current required by its load within its limits.
- Gain and maximum clean output are different specifications.
- The simple voltage-squared power calculation assumes a resistive load.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
