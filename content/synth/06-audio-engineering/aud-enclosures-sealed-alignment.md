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

A rough rule of thumb uses the **efficiency bandwidth product** (EBP):

```formula
EBP = Fs / Qes
EBP = 30 Hz / 0.5
EBP = 60 Hz
where
EBP: the efficiency bandwidth product, in hertz (Hz)
Fs: the free-air resonance, in hertz (Hz); here 30 Hz
Qes: the electrical Q (no unit); here 0.5
Hz: hertz, cycles per second
In words: drivers with an EBP around 50 tend to suit sealed boxes and those around 100 suit ported ones.
```

An EBP of 60 Hz sits near the sealed end. It's a starting point, not a design method: always model the full parameter set.

Manufacturing tolerances are loose: Purdue's notes give typical factory tolerances of about ±15% for Fs and ±20–30% for Vas. Measure your own driver if accuracy matters.

### The sealed-box equations

Put a driver in a sealed box. The air trapped in the box is a second spring pushing on the cone, alongside the suspension. A smaller box is a stiffer spring. The **compliance ratio** says how stiff the box air is compared with the suspension, and both the resonance and its Q rise with the square root of the total stiffness. These are the closed-box results (Small, 1972), used when you choose a box size:

```formula
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
In words: a smaller box (bigger α) pushes the resonance up and makes it less damped, both by the same factor √(1 + α).
```

Consider a driver with 30 Hz free-air resonance, total Q of 0.35 and 60 L equivalent compliance volume, in a 20 L box:

```formula
α = 60 L / 20 L = 3
√(1 + α) = √(4) = 2
Fc = 30 Hz × 2 = 60 Hz
Qtc = 0.35 × 2 = 0.70
where
α: alpha, the compliance ratio (no unit)
√: square root
L: litre, a unit of volume
Fc: the in-box resonance, in hertz (Hz)
Qtc: the in-box total Q (no unit)
Hz: hertz, cycles per second
In words: a 20 L box makes this driver resonate at 60 Hz with a Q of 0.70, close to maximally flat.
```

These equations ignore box losses and stuffing, and they assume the box is small compared with the wavelength (true in the bass).

The sealed-box **total Q** sets the shape of the bass roll-off. The box-and-driver is a second-order high-pass filter, and for that filter the level exactly at Fc depends only on Qtc:

```formula
L_Fc = 20 log_10(Qtc)
L_Fc = 20 log_10(0.707)
L_Fc ≈ −3 dB
where
L_Fc: the response at Fc, relative to the flat level well above Fc, in decibels (dB)
Qtc: the in-box total Q (no unit); here 0.707
log_10: the base-10 logarithm: log_10(x) is the power you raise 10 to in order to get x
≈: approximately equal to
dB: decibel, a logarithmic unit for comparing levels
In words: A total Q of 0.5 gives −6 dB at resonance, 0.707 gives −3 dB, and 1.0 gives 0 dB with a hump above resonance.
```

| Qtc | Behaviour |
|---|---|
| 0.5 | Critically damped, −6 dB at Fc |
| 0.707 | Butterworth: maximally flat, −3 dB at Fc |
| ~1.0–1.1 | Peak before roll-off, "boomier" |

The same sum for three box sizes, as code:

```python
import math

def sealed(fs, qts, vas, vb):
    a = vas / vb
    # Box air raises resonance and total Q.
    k = math.sqrt(1 + a)
    return fs * k, qts * k

for vb in (10, 20, 40):
    fc, qtc = sealed(30, 0.35, 60, vb)
    print(f"{vb:>2} L: Fc={fc:5.1f} Hz,"
          f" Qtc={qtc:.2f}")
```

```
10 L: Fc= 79.4 Hz, Qtc=0.93
20 L: Fc= 60.0 Hz, Qtc=0.70
40 L: Fc= 47.4 Hz, Qtc=0.55
```

The 20 L box gives a near-Butterworth alignment (a Qtc of about 0.7) with a 60 Hz resonance. A smaller box gives higher, peakier bass; a bigger one lower, more damped bass. Deep bass extension, reference efficiency and enclosure volume are coupled. “Pick two” summarizes the trade-off; real driver excursion, losses and power limits still constrain the design.

(Filling the box with absorbent material can make it behave as if it were somewhat larger: Purdue's notes say up to about 15% in apparent volume, while also adding some effective moving mass.)

## Key takeaways
- Efficiency bandwidth product is only an initial enclosure-selection guide.
- A smaller sealed box raises both resonance and Q in the ideal model.
- Real losses, stuffing and measured driver parameters affect the finished alignment.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
