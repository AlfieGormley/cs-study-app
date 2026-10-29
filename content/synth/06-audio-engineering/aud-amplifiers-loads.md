---
id: aud-amplifiers-loads
title: Parallel loads and bridged outputs
level: advanced
minutes: 4
summary: Lower impedance demands greater current at the same output voltage.
sourceLesson: aud-amplifiers
---

## Load impedance and matching amp to speaker

A solid-state amp is a voltage source, so **lower impedance draws more current and more power**. The voltage that gives 100 W into 8 Ω (about 28 V RMS, pushing about 3.5 A) would push twice the current, about 7 A, into 4 Ω: ideally twice the power, 200 W.

That's why amplifiers quote power at several loads ("100 W into 8 Ω, 160 W into 4 Ω"). In practice power doesn't quite double into half the impedance, because the supply sags and the output devices have current limits.

Matching rules of thumb:

- **Check the minimum load.** If an amp is rated for 4 Ω minimum, don't connect two 4 Ω speakers in parallel (2 Ω). Speakers' actual impedance dips below nominal (the loudspeaker-driver units), so nominal 4 Ω loads are already demanding.
- **Parallel speakers halve impedance** (two 8 Ω = 4 Ω); series doubles it.
- **Power headroom.** An amplifier’s clean capacity should accommodate the required peaks, but a higher rating can also destroy a driver. Avoid clipping and set gain and appropriate protection from the actual signal, driver limits and manufacturer’s guidance. Many manufacturers give a recommended amplifier power range; follow it.
- **Bridged (BTL) mode** drives one speaker from two channels in opposite polarity, doubling the voltage swing: in theory four times the power into the same load, but each channel sees half the load impedance, so bridging into 4 Ω asks each side to drive 2 Ω. Check the manual's bridged minimum load.

For unequal speakers in parallel, the combined impedance is always below the lower of the two:

```formula reference
R_par = (R_1 R_2) / (R_1 + R_2)
where
R_par: the combined resistance of two loads in parallel, in ohms (Ω)
R_1: the first speaker's impedance, in ohms (Ω)
R_2: the second speaker's impedance, in ohms (Ω)
Ω: ohms
In words: Two loads in parallel combine to their product divided by their sum, which is always less than either one; two equal speakers give half the impedance of one.
```

> [!tip] Valve amplifiers are different
> Valve amplifiers with output transformers *do* need the right load: running them with no speaker connected can damage the output transformer or valves. Always connect a speaker (or a proper load) before powering a valve guitar or hi-fi amp.

## Key takeaways
- Lower impedance demands greater current at the same output voltage.
- Two identical parallel speaker loads have half the impedance of one.
- Bridging doubles voltage swing ideally while each channel effectively drives half the load impedance.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Example valve-amplifier load warning — Fender 65 Twin Reverb manual, rear panel](https://www.fmicassets.com/Damroot/Original/10001/021730_gamp_manual_all_revE.pdf)
