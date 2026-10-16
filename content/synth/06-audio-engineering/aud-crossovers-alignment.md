---
id: aud-crossovers-alignment
title: Align drivers and protect the tweeter
level: advanced
minutes: 4
summary: Distance offsets create frequency-dependent phase error.
sourceLesson: aud-crossovers
---

## Driver offset and phase

The preceding units’ ideal sums assume both drivers' sound starts from the same point. Real drivers don't: a woofer's **acoustic centre** usually sits further back than a tweeter's on a flat baffle. A path difference becomes a time delay, and a time delay becomes a frequency-dependent phase shift that ruins the neat summation:

```formula
t = d / c
φ = 360°ft
t = 0.02 m / (343 m/s) ≈ 58 µs
t = 0.08 m / (343 m/s) ≈ 233 µs
φ = 360° × 2000 Hz × 233 µs ≈ 168°
where
t: the time delay between the two drivers' sound, in seconds (s) or microseconds (µs, millionths of a second)
d: the path difference: how much further one acoustic centre is from the listener, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
φ: the phase error the delay causes, in degrees (°); 360° is one whole cycle
f: the frequency in question, here the 2 kHz crossover, in hertz (Hz)
m: metres
s: seconds
µs: microseconds
Hz: hertz, cycles per second
≈: approximately equal to
In words: sound covers about 3.4 mm every 10 µs, and a fixed delay is a bigger slice of a cycle at higher frequencies; 233 µs is almost half a 2 kHz cycle (500 µs).
```

The script below adds that delay to the woofer of an ideal 2 kHz LR4 crossover and prints the on-axis sum in dB.

```python
import cmath, math

def lr4(f, fc):
    s = 1j * f / fc
    # Square each Butterworth transfer.
    d = s * s + math.sqrt(2) * s + 1
    return 1 / d**2, s**4 / d**2

def summed_db(f, fc, lag=0.0):
    lp, hp = lr4(f, fc)
    # woofer (low-pass) arrives late
    lp *= cmath.exp(-2j * math.pi * f * lag)
    db = 20 * math.log10(abs(lp + hp))
    return round(db, 1) + 0.0

fc = 2000
print("  f     0cm   2cm   8cm")
for f in (500, 1000, 1500, 2000,
          2500, 4000):
    row = [summed_db(f, fc, cm / 100 / 343)
           for cm in (0, 2, 8)]
    print(f"{f:>5}" + "".join(
        f"{v:6.1f}" for v in row))
```

```
  f     0cm   2cm   8cm
  500   0.0   0.0   0.0
 1000   0.0   0.0  -0.5
 1500   0.0  -0.2  -3.8
 2000   0.0  -0.6 -19.6
 2500   0.0  -0.8  -6.4
 4000   0.0  -0.5   0.0
```

With the woofer 2 cm behind (58 µs), the dip is under 1 dB. At 8 cm (233 µs, almost half a period at 2 kHz) there's a deep on-axis hole at the crossover. Remedies:

- **DSP delay** on the earlier driver (easy in active/DSP systems).
- **Stepped or sloped baffles** to line up acoustic centres physically.
- Choosing the crossover frequency and filter shapes so the *acoustic* responses (filter × driver) hit the target, and checking the result by measurement.

Even when on-axis is perfect, moving up or down changes the path lengths to the two drivers. That's **lobing**: the summed response changes with vertical angle. LR crossovers with aligned drivers keep the main radiation lobe pointing straight ahead, which is one reason they're popular.

## Filter choice also protects a driver

The first-order and LR4 filters from the preceding units pass very different amounts of signal below the crossover. At half the crossover frequency, the ideal first-order high-pass is about seven decibels down, while LR4 is about twenty-five decibels down. The question works through the transfer-function calculation.

This reduces the tweeter’s out-of-band input for the same source level. It does not establish a safe crossover or power rating: use the exact driver’s recommended filter type, minimum crossover and excursion and thermal limits, then measure the acoustic result.

## Key takeaways
- Distance offsets create frequency-dependent phase error.
- Delay or physical alignment can improve the target-axis sum.
- Steeper high-pass attenuation reduces out-of-band tweeter input but does not establish safe operating power.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
