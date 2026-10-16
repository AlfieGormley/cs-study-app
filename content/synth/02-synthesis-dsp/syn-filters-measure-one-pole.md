---
id: syn-filters-measure-one-pole
title: Measuring the one-pole frequency response
level: intermediate
minutes: 5
summary: Measuring the one-pole frequency response.
sourceLesson: syn-filters
---

```python
import math

class OnePoleLP:
    def __init__(self, fc, fs):
        w = 2 * math.pi * fc / fs
        self.a = 1.0 - math.exp(-w)
        self.y = 0.0       # the state

    def process(self, x):
        # Previous output persists in this
        # object.
        self.y += self.a * (x - self.y)
        return self.y

fs = 48000
for f in (100, 1000, 4000, 16000):
    lp = OnePoleLP(1000, fs)
    peak = 0.0
    for n in range(fs // 2):       # 0.5 s
        w = 2 * math.pi * f * n / fs
        y = lp.process(math.sin(w))
        if n > fs // 4:            # settled
            peak = max(peak, abs(y))
    # Unit input peak: ratio equals output
    # peak.
    db = 20 * math.log10(peak)
    print(f, round(db, 1))
```

```
100 -0.0
1000 -3.0
4000 -12.2
16000 -22.5
```

This is the roadmap exercise "measure its effect at selected frequencies": feed in sines and measure what comes out. Theory gives the same answers. The filter's magnitude response is:

```formula
|H| = a / |1 − (1 − a) × e^{(−jω)}|
ω = (2πf) / f_s
where
|H|: the filter's gain at frequency f (output amplitude divided by input amplitude); 20 log_10 of it gives decibels
a: the coefficient, here 0.1227
e^{(−jω)}: a complex number of size 1 at angle −ω; it stands for a one-sample delay at this frequency
e: Euler's number, about 2.71828
j: the imaginary unit, the square root of −1 (engineers write j rather than i)
ω: omega, the frequency as an angle per sample, in radians per sample
π: pi, about 3.14159
f: the input frequency, in hertz (Hz)
f_s: the sample rate, in Hz
|x|: the magnitude (size) of a number, ignoring its sign or angle
In words: the gain is a divided by the size of a complex number that grows with frequency, so higher frequencies come out quieter; at 1 kHz with a = 0.1227 it is about 0.708, which is −3.0 dB.
```

The complex response predicts the steady sine amplitude; the peak-of-samples method can differ at the displayed precision, and filling in more points gives the table below. Measuring only the largest sample is generally phase-dependent; for more accurate sine amplitude estimates, fit sine/cosine coefficients or measure RMS over complete cycles.

| Input | Gain (1 kHz cutoff) |
|---|---|
| 500 Hz | −1.0 dB |
| 1 kHz | −3.0 dB |
| 2 kHz | −7.0 dB |
| 4 kHz | −12.2 dB |
| 8 kHz | −17.7 dB |
| 16 kHz | −22.5 dB |

The slope settles towards about 6 dB per octave above cutoff, then flattens as it approaches Nyquist (the digital filter is not an exact copy of an analogue one up there).

> [!warning] Cutoff accuracy at high frequencies
> The `exp` formula puts the −3 dB point very close to the set cutoff when the cutoff is well below Nyquist. At 48 kHz the half-power point (about −3.01 dB) is about 1,001.43 Hz for a 1 kHz setting, 5,188.89 Hz for 5 kHz, and 11.895 kHz for 10 kHz. A 15 kHz setting never reaches half power below Nyquist. A literal −3.000 dB crossing is slightly different; the usual “−3 dB cutoff” label is a rounded half-power convention. If you need accurate high cutoffs, use a design based on the bilinear transform with prewarping (as the RBJ cookbook does).

The same structure gives a **one-pole high-pass** for free:

```formula
y_hp[n] = x[n] − y_lp[n]
where
y_hp[n]: the high-pass output at sample n
x[n]: the input at sample n
y_lp[n]: the one-pole low-pass output at sample n
In words: whatever the low-pass keeps, the high-pass removes, so subtracting the low part from the input leaves the high part.
```

With a very low cutoff (a few hertz) that is a **DC blocker**, handy for removing the offset from a pulse wave.

## Key takeaways

- Measure settled sines and compare with the response formula.
- The exponential coefficient approximates the intended cutoff only well below Nyquist.
- Subtracting low-pass output produces a DC-rejecting high-pass, with a design-dependent gain.

## Further reading

- [One-pole filter — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/One_Pole.html)
- [One-pole filter — Nigel Redmon](https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/)
- [Audio EQ Cookbook — Robert Bristow-Johnson / W3C](https://www.w3.org/TR/audio-eq-cookbook/)
