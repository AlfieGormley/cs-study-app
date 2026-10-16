---
id: syn-bandlimited-polyblep-experiment
title: A measured PolyBLEP saw experiment
level: intermediate
minutes: 5
summary: A measured PolyBLEP saw experiment.
sourceLesson: syn-bandlimited
---

This is an offline NumPy experiment requiring NumPy installed in the Python environment. All subsequent NumPy experiments use the same dependency. The test is one second at a fixed integer frequency, so the FFT bins are one hertz apart. It compares this polynomial implementation, not a proof about every BLEP library or about modulated notes.

## A PolyBLEP saw in Python

The polynomial below is the widely circulated two-sample PolyBLEP (as used in Martin Finke's tutorial). Written as maths first:

```formula
y = 2p − 1 − B
B = 2u − u^2 − 1,  u = p / dt
B = u^2 + 2u + 1,  u = (p − 1) / dt
where
y: the corrected saw output sample
p: the phase, from 0 up to 1, in cycles
B: the PolyBLEP correction: use the first formula when p < dt (the sample just after the jump), the second when p > 1 − dt (the sample just before it), and B = 0 otherwise
u: how far the sample is from the jump, measured in samples: between 0 and 1 just after it, between −1 and 0 just before it
dt: the phase increment per sample (f_0 / f_s), as in the code
f_0: the note's frequency, in hertz
f_s: the sample rate, in hertz
<, >: less than, greater than
In words: away from the jump the saw is untouched; on the one sample either side of the jump, a small curve is subtracted that replaces the instant drop with a short smooth approximation with reduced aliasing, not an ideal strictly band-limited step.
```

For the numeric half-sample example, a phase of 0.05 cycles with an increment of 0.1 gives a rescaled distance of 0.5. The correction is −0.25, so the corrected sample is −0.65 rather than the naive −0.9. The question’s worked card shows the substitution. The code assumes constant positive frequency strictly below Nyquist, finite values, and one sample-loop evaluation per output sample:

```python
import numpy as np

def poly_blep(t, dt):
    # t: phase [0,1), dt: increment
    if t < dt:             # just after jump
        t = t / dt
        return t + t - t * t - 1.0
    if t > 1.0 - dt:       # just before
        t = (t - 1.0) / dt
        return t * t + t + t + 1.0
    return 0.0

def saw(f0, fs, n, blep):
    dt, p = f0 / fs, 0.0
    out = np.zeros(n)
    for i in range(n):
        y = 2.0 * p - 1.0
        if blep:
            # Falling edge: subtract
            # correction.
            y -= poly_blep(p, dt)
        out[i] = y
        p += dt
        if p >= 1.0:
            p -= 1.0
    return out

fs, f0 = 48000, 1245     # 1 s: bin = 1 Hz
k = np.arange(fs // 2 + 1)

# Only multiples of f0 are wanted harmonics.
harm = (k % f0 == 0) & (k > 0)
low = (k > 0) & (k < 10000)
for blep in (False, True):
    x = saw(f0, fs, fs, blep)
    X = np.abs(np.fft.rfft(x)) * 2 / fs
    # Search off-harmonic bins below 10 kHz.
    alias = np.where(~harm & low, X, 0)
    w = np.argmax(alias)
    db = 20 * np.log10(alias[w] / X[f0])
    # Droop versus the ideal tenth harmonic.
    h10 = 20 * np.log10(X[10 * f0] * 10
                        / X[f0])
    print("polyblep" if blep else "naive",
          w, round(db, 1), round(h10, 1))
```

Output:

```
naive 9405 -29.8 0.0
polyblep 9405 -55.4 -1.9
```

Reading it: the strongest alias below 10 kHz is at 9,405 Hz in both cases (harmonic 31 folded), but PolyBLEP pushes it from −29.8 dB to −55.4 dB relative to the fundamental, an improvement of about 25 dB. The last column is the 10th harmonic (12,450 Hz) relative to its ideal the reciprocal of harmonic number level: PolyBLEP softens it by 1.9 dB. In the same run the 19th harmonic (23.7 kHz) was 7.6 dB low. That is PolyBLEP's trade-off: it gently dulls the very top octave while removing most of the audible aliasing.

## Key takeaways

- Evaluate the correction relative to the edge and subtract it for a falling saw edge.
- Measure residual aliases and wanted-harmonic droop together.

## Further reading

- [Oscillator implementation — DaisySP](https://raw.githubusercontent.com/electro-smith/DaisySP/2c72eaf9eac5fc0dca1919d65d606da907832618/Source/Synthesis/oscillator.cpp)
- [finke](https://www.martin-finke.de/articles/audio-plugins-018-polyblep-oscillator/)
- [Real FFT — NumPy](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
