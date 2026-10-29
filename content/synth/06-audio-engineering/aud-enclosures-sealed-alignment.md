---
id: aud-enclosures-sealed-alignment
title: Estimate a sealed box’s resonance and Q
level: intermediate
minutes: 5
summary: Efficiency bandwidth product is only an initial enclosure-selection guide.
sourceLesson: aud-enclosures
---

## Driver choice and sealed-box alignment

### Efficiency bandwidth product

A rough first sort uses the **efficiency bandwidth product** (EBP): the free-air resonance divided by the electrical Q. Purdue's rule of thumb is that drivers with an EBP around 50 tend to suit sealed boxes and those around 100 suit ported ones. A driver with a high resonance and a strong motor (low electrical Q) therefore leans towards ported. It's a starting point, not a design method: always model the full parameter set.

```formula reference
EBP = Fs / Qes
where
EBP: the efficiency bandwidth product, in hertz (Hz)
Fs: the free-air resonance, in hertz (Hz)
Qes: the electrical Q (no unit)
Hz: hertz, cycles per second
In words: Divide the free-air resonance by the electrical Q; values around 50 suggest a sealed box and around 100 a ported one, as a first guess only.
```

Manufacturing tolerances are loose: Purdue's notes give typical factory tolerances of about ±15% for Fs and ±20–30% for Vas. Measure your own driver if accuracy matters.

### The sealed-box relationships

Put a driver in a sealed box. The air trapped in the box is a second spring pushing on the cone, alongside the suspension. A smaller box is a stiffer spring. The **compliance ratio** says how stiff the box air is compared with the suspension, and both the resonance and its Q rise with the square root of the total stiffness. These closed-box results (Small, 1972) are the core of choosing a box size:

```formula reference
α = Vas / Vb
Fc = Fs √(1 + α)
Qtc = Qts √(1 + α)
where
α: alpha, the compliance ratio (no unit): how many times stiffer the box air is than the driver's suspension
Vas: the driver's equivalent compliance volume, in litres (L)
Vb: the internal volume of the box, in litres (L)
Fc: the resonance frequency of the driver in the box, in hertz (Hz)
Fs: the driver's free-air resonance, in hertz (Hz)
Qtc: the total Q of the driver in the box (no unit); it sets the shape of the bass roll-off
Qts: the driver's total Q in free air (no unit)
√: square root
L: litre, a unit of volume; 1 L = 0.001 m^3
Hz: hertz, cycles per second
In words: The smaller the box compared with the driver's Vas, the stiffer the trapped air, and the more the resonance and the Q in the box both rise above the driver's free-air values, by the same factor.
```

The important consequence is that **resonance and Q move together**. You cannot make a sealed box smaller without also raising its resonance and making it peakier, and a bigger box gives lower, more damped bass. These relationships ignore box losses and stuffing, and they assume the box is small compared with the wavelength (true in the bass).

The sealed-box **total Q** sets the shape of the bass roll-off. The box-and-driver is a second-order high-pass filter, and the level exactly at Fc depends only on Qtc:

| Qtc | Behaviour |
|---|---|
| 0.5 | Critically damped, −6 dB at Fc |
| 0.707 | Butterworth: maximally flat, −3 dB at Fc |
| ~1.0–1.1 | Peak before roll-off, "boomier" |

For example, take a driver with a 30 Hz free-air resonance, total Q of 0.35 and a 60 L equivalent compliance volume:

| Box | Fc | Qtc | Character |
|---|---|---|---|
| 10 L | about 79 Hz | about 0.93 | peaky, less deep |
| 20 L | 60 Hz | 0.70 | near-Butterworth |
| 40 L | about 47 Hz | about 0.55 | deeper, well damped |

Deep bass extension, reference efficiency and enclosure volume are coupled. “Pick two” summarizes the trade-off; real driver excursion, losses and power limits still constrain the design.

(Filling the box with absorbent material can make it behave as if it were somewhat larger: Purdue's notes say up to about 15% in apparent volume, while also adding some effective moving mass.)

## Key takeaways
- Efficiency bandwidth product is only an initial enclosure-selection guide.
- A smaller sealed box raises both resonance and Q in the ideal model.
- Real losses, stuffing and measured driver parameters affect the finished alignment.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
