---
id: aud-amplifiers-loads
title: Parallel loads and bridged outputs
level: advanced
minutes: 4
summary: Lower impedance demands greater current at the same output voltage.
sourceLesson: aud-amplifiers
---

## Load impedance and matching amp to speaker

A solid-state amp is a voltage source, so **lower impedance draws more current and more power**:

```formula
V_rms = √(PR)
V_rms = √(100 W × 8 Ω) ≈ 28.3 V
I_rms = 28.3 V / 8 Ω ≈ 3.5 A
P = (28.3 V)^2 / 4 Ω ≈ 200 W
I_rms = 28.3 V / 4 Ω ≈ 7.1 A
where
V_rms: the RMS output voltage, in volts (V)
P: the average power into the load, in watts (W)
R: the load resistance, in ohms (Ω)
I_rms: the RMS current, in amperes (A)
√: square root
≈: approximately equal to
V: volts
W: watts
Ω: ohms
A: amperes
In words: the voltage that gives 100 W into 8 Ω would push twice the current, and so twice the power, into 4 Ω.
```

That's why amps quote power at several loads ("100 W into 8 Ω, 160 W into 4 Ω"). In practice power doesn't quite double into half the impedance, because the supply sags and the output devices have current limits.

Matching rules of thumb:

- **Check the minimum load.** If an amp is rated for 4 Ω minimum, don't connect two 4 Ω speakers in parallel (2 Ω). Speakers' actual impedance dips below nominal (the loudspeaker-driver units), so nominal 4 Ω loads are already demanding.
- **Parallel speakers halve impedance** (two 8 Ω = 4 Ω); series doubles it.
- **Power headroom.** An amplifier’s clean capacity should accommodate the required peaks, but a higher rating can also destroy a driver. Avoid clipping and set gain and appropriate protection from the actual signal, driver limits and manufacturer’s guidance. Many manufacturers give a recommended amplifier power range; follow it.
- **Bridged (BTL) mode** drives one speaker from two channels in opposite polarity, doubling the voltage swing: in theory four times the power into the same load, but each channel sees half the load impedance, so bridging into 4 Ω asks each side to drive 2 Ω. Check the manual's bridged minimum load.

The parallel and bridged rules come from these relations (for resistive loads):

```formula
R_par = (R_1 R_2) / (R_1 + R_2)
R_par = (8 Ω × 8 Ω) / (8 Ω + 8 Ω) = 4 Ω
P_bridge = (2V)^2 / R = 4V^2 / R
R_ch = R / 2
where
R_par: the combined resistance of two loads in parallel, in ohms (Ω)
R_1: the first speaker's impedance, in ohms (Ω)
R_2: the second speaker's impedance, in ohms (Ω)
P_bridge: the power into the speaker in bridged mode, in watts (W)
V: the RMS voltage one channel can swing on its own, in volts (V)
R: the bridged speaker's impedance, in ohms (Ω)
R_ch: the load each channel effectively sees in bridged mode, in ohms (Ω)
Ω: ohms
In words: two equal speakers in parallel give half the impedance; bridging doubles the voltage, so in theory four times the power, but each channel then works as if it were driving half the speaker's impedance.
```

> [!tip] Valve amps are different
> Valve amps with output transformers *do* need the right load: running them with no speaker connected can damage the output transformer or valves. Always connect a speaker (or a proper load) before powering a valve guitar or hi-fi amp.

## Key takeaways
- Lower impedance demands greater current at the same output voltage.
- Two identical parallel speaker loads have half the impedance of one.
- Bridging doubles voltage swing ideally while each channel effectively drives half the load impedance.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Example valve-amplifier load warning — Fender 65 Twin Reverb manual, rear panel](https://www.fmicassets.com/Damroot/Original/10001/021730_gamp_manual_all_revE.pdf)
