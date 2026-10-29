---
id: aud-drivers-response-and-limits
title: Driver response, dispersion and limits
level: intermediate
minutes: 5
summary: A larger piston becomes directional at a lower frequency.
sourceLesson: aud-drivers
---

## Frequency response

A frequency response plot shows on-axis SPL (at a fixed input) against frequency. Look for:

- The **usable range**, often given as ±3 dB limits, with the low-frequency limit set mainly by Fs and the enclosure.
- **Smoothness**: narrow peaks often come from cone breakup or cabinet resonance.
- **Off-axis curves**: how the response changes at 30° or 60°. Because of diffraction, a driver radiates widely when its wavelength is large compared with the cone, and shows **beaming** (narrower dispersion) when the wavelength becomes comparable with the cone.

Where does beaming start? Treat the cone as a flat, rigid disc (a "piston"). Directivity becomes significant roughly when the cone's circumference reaches one wavelength. So the bigger the cone, the lower the frequency at which it starts beaming: double the radius and beaming starts an octave lower.

```formula reference
f_beam = c / (2πa)
where
f_beam: the frequency above which the cone starts to focus sound forwards instead of spreading it, in hertz (Hz)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
π: pi, about 3.14159
a: the effective radius of the cone (half its effective diameter), in metres (m)
Hz: hertz, cycles per second
In words: In the rigid-piston model, beaming becomes significant when the cone's circumference is about one wavelength, so a cone of twice the radius starts beaming an octave lower.
```

For a woofer with a 13 cm effective diameter this gives about 840 Hz; for a 25 mm tweeter dome, about 4.4 kHz, roughly five times higher because the dome is roughly five times smaller. The piston model stops being reliable once the cone breaks up (below), so check measured off-axis curves.

That beaming is one reason multi-way speakers hand high frequencies to smaller drivers.

## Power handling

Two separate limits:

- **Driver power handling** (thermal). The voice coil heats up. Too much *average* power for too long burns the coil or its adhesive. Ratings are usually based on long tests with band-limited noise, and the method (and so the number) differs between standards and manufacturers, so read what method a figure refers to.
- **Mechanical (excursion).** At low frequencies the cone must move a long way. **Xmax** describes an excursion limit under a specified geometric or distortion criterion; definitions vary. Motor, suspension and other nonlinearities can limit it. Beyond the useful linear range, distortion increases; far beyond it, the coil can strike the motor structure or the suspension can tear. A driver can be over-excursed at low frequencies with modest power, especially below a ported box's tuning frequency (the enclosure units).

> [!tip] Power ratings are not targets
> A "100 W" speaker doesn't need 100 W, and isn't safe with any 100 W signal. A clipped signal from a small amplifier can damage a tweeter (the power-amplifier units), while the required clean peak capacity and suitable protection must be chosen from actual limits.

## Driver types

| Driver | Typical job | Notes |
|---|---|---|
| Subwoofer | Below ~80–120 Hz | Long excursion, big cone |
| Woofer | Bass (and mids in 2-way) | 13–38 cm common |
| Midrange | ~300 Hz–3 kHz | Covers the vocal region |
| Tweeter | Above ~2–3 kHz | Light dome, 19–28 mm |
| Compression driver + horn | Mid/high in PA | Very high sensitivity |

In a **compression driver**, a diaphragm pressurises a small chamber; sound passes through **phase-plug** channels into a narrow **horn throat**, and the **loudspeaker horn** flares out to the room. The horn improves the match between the diaphragm and the air, so far more of the electrical power becomes sound. It also controls dispersion, which PA designers use to aim sound at the audience and away from walls. Horn-loaded systems can reach sensitivities around 110 dB SPL at 2.83 V/1 m; a typical hi-fi speaker is in the mid-80s to around 90 dB.

## Cone breakup

At low frequencies a cone moves as a rigid **rigid piston**. As frequency rises, the cone stops moving as one piece: bending waves travel across it, and different parts move with different phase. This is **cone breakup**. It causes:

- Peaks and dips in the response, often a sharp peak near the top of the driver's range.
- Changes in dispersion, and sometimes audible coloration and distortion.

Stiff, light cones (aluminium, ceramic) push breakup higher but often produce a stronger, sharper peak when it happens. Softer, well-damped cones break up earlier but more gently. Either way, the crossover (the crossover units) is chosen so the driver isn't asked to play much in its breakup region.

## Key takeaways
- A larger piston becomes directional at a lower frequency.
- Cone breakup invalidates a rigid-piston prediction; use measured off-axis data.
- Thermal power and cone excursion are separate limits.
- Driver types trade displacement, bandwidth, dispersion and efficiency.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
