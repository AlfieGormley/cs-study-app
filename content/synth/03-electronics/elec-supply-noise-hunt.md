---
id: elec-supply-noise-hunt
sourceLesson: elec-noise-grounding
title: "Supply noise, rejection and a diagnostic checklist"
level: advanced
minutes: 2
summary: "Compare supplies methodically and follow documented decoupling and filtering."
---

Compare supplies methodically and follow documented decoupling and filtering.

## Power supply noise and decoupling
A synth's supply often comes from a computer's USB port or a USB charger. Both carry noise: digital load current from the computer, and supply ripple at the supply-switching rate of switch-mode chargers and regulators.

How it reaches the audio:

- Op-amps, codecs and regulators reject supply noise only partially. Their **power supply rejection ratio (PSRR)** typically falls as frequency rises, so high-frequency supply noise gets through more easily. Datasheets show this as a "PSRR vs frequency" graph; TI’s OPA1612 datasheet SBOS450C (revision C, August 2014; checked 29 October 2026) has an example (its "CMRR and PSRR vs Frequency" figure).
- Digital chips on the same rail inject current spikes, which the local decoupling capacitors described earlier help contain.

Defences, in order of effort:

1. **Follow each chip’s decoupling requirements** with short supply paths and current return paths, plus specified bulk storage at power entry. 100 nF is the SN74HC00 example, not a universal bill of materials.
2. **Use the documented analogue-supply filtering.** An RC filter loses DC voltage as load current rises; an LC network can resonate. Check load current, available DC voltage, damping and regulator stability before adding either.
3. **Use a dedicated low-noise linear regulator** if the board design calls for it, with adequate input-to-output voltage difference, heat dissipation and the specified input/output capacitors.
4. **Use a better source:** try a different USB supply or a battery bank to see whether the noise follows the supply.

Audio-focused development boards often build these measures in. Read the board's documentation before adding your own. Your main job is not to undo them with poor external wiring.

## A noise-hunting checklist
- Identify the noise: steady 50/100 Hz hum (ground loop or mains field), or whine that tracks computer, LED or processor activity (digital ground or supply noise).
- Remove connections one at a time and note what changes.
- Try battery power for the synth.
- Check that audio grounds return directly to the board's ground, not through LED or digital wiring.
- Confirm decoupling capacitors are present and close to their pins.
- Use balanced or isolated connections between devices where possible.
- Never remove a mains safety earth.

## Key takeaways

- Compare supplies methodically and follow documented decoupling and filtering.
- A battery test implicates changed paths; it does not prove a unique cause.

## Further reading

- [Analog Devices MT-101: decoupling techniques](https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf)
- [TI OPA1612: PSRR versus frequency](https://www.ti.com/lit/ds/symlink/opa1612.pdf)
- [Analog Devices MT-031: converter grounding](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)
- [TI SLVA519: output-filter choices and regulator stability](https://www.ti.com/lit/an/slva519/slva519.pdf)
