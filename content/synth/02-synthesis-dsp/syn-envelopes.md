---
id: syn-envelopes
title: Envelopes and parameter smoothing
level: intermediate
minutes: 14
summary: ADSR envelopes with linear and exponential (one-pole) segments, retriggering, clicks and legato, plus parameter smoothing to remove zipper noise and how to choose smoothing times.
---

A note isn't just a pitch and a timbre; it has a shape in time. A piano note strikes and decays, an organ note starts and stops abruptly, a pad swells. The **envelope** generates that shape as a control signal, usually driving the amplifier (loudness) and often the filter cutoff (brightness).

The same maths solves a second problem: when a knob or MIDI controller changes a parameter in steps, the audio must not step with it. That's **parameter smoothing**.

## ADSR

The classic envelope has four controls, triggered by the key's **gate** (on while held):

- **Attack:** time to rise from the current level to the peak after the key goes down.
- **Decay:** time to fall from the peak to the sustain level.
- **Sustain:** a *level* (not a time), held while the key stays down.
- **Release:** time to fall to zero after the key is released.

```diagram
level
 1.0 |   /\
     |  /  \___________  <- sustain
     | /               \
 0.0 |/                 \____
     +--A--D-----S------R---> time
     gate on      gate off
```

### Linear segments

The simplest implementation moves the level by a fixed step per sample. For an attack from 0 to 1 the step is the total rise divided by the number of samples the attack lasts:

```formula
Δy = 1 / (T_a × f_s)
Δy = 1 / (0.01 s × 48000 Hz) = 1 / 480
where
Δy: delta y, how much the level rises each sample
T_a: the attack time, in seconds (s); here 10 ms = 0.01 s
f_s: the sample rate, in hertz (Hz): samples per second, here 48,000
s: seconds
Hz: hertz, per second
In words: spread the rise from 0 to 1 evenly over the attack's samples; a 10 ms attack at 48 kHz lasts 480 samples, so each adds 1/480.
```

Decay and release work the same way, using the distance they have to travel. It's easy to reason about, and each segment ends at a precise time.

Linear segments have a drawback for amplitude: hearing is roughly logarithmic, so a linear fade in *amplitude* sounds like it hangs on, then vanishes abruptly at the end. Linear attacks often sound fine; linear releases and decays often sound unnatural.

### Exponential (one-pole) segments

Analogue envelope generators charge and discharge a capacitor through a resistor, which gives exponential curves. Digitally, that is a **one-pole filter** moving towards a target: each sample, the level moves a fixed fraction of the remaining distance.

```formula
y[n] = y[n−1] + c × (g − y[n−1])
c = 1 − exp(−1 / (τ × f_s))
c = 1 − exp(−1 / (0.01 s × 48000 Hz))
c = 1 − exp(−1/480) ≈ 0.00208
where
y[n]: the envelope level at sample n; y[n−1] is the level one sample earlier
c: the coefficient: the fraction of the remaining distance covered each sample, between 0 and 1
g: the target level the segment is heading for (the peak, the sustain level or 0)
exp: the exponential function, e raised to a power, where e ≈ 2.71828
τ: tau, the time constant, in seconds (s); here 10 ms = 0.01 s
f_s: the sample rate, in hertz (Hz), here 48,000
s: seconds
Hz: hertz, per second
≈: approximately equal to
In words: each sample the level closes a small fixed fraction of the gap to the target, so it moves fast when far away and slows as it gets close; a longer time constant means a smaller fraction and a slower curve.
```

In the code this is `y += c * (target - y)`. The coefficient is chosen so that the remaining distance shrinks by a factor of e every τ seconds. `tau` (τ) is the **time constant**: after τ seconds the level has covered 63.2% of the distance to the target. In general:

```formula
r(t) = 1 − exp(−t / τ)
t = τ × ln(1 / (1 − r))
r = 0.99: t = τ × ln(100) ≈ 4.6 × τ
where
r(t): the fraction of the distance to the target covered after time t, from 0 to 1
t: the time since the segment started, in seconds (s)
τ: tau, the time constant, in seconds
exp: the exponential function, e raised to a power (e ≈ 2.71828)
ln: the natural logarithm, the inverse of exp: ln(exp(x)) = x
r: the fraction you want to reach, e.g. 0.99 for 99%
≈: approximately equal to
s: seconds
In words: after one time constant the level is 63.2% of the way there (1 − 1/e); reaching 99% takes about 4.6 time constants and 99.9% about 6.9.
```

Measured at 48 kHz with τ = 10 ms:

| Fraction reached | Time |
|---|---|
| 63.2% | 10.0 ms |
| 99% | 46.1 ms (4.6 τ) |
| 99.9% | 69.1 ms (6.9 τ) |

An exponential approach never quite arrives, which creates two practical issues:

1. **Attack:** if the target is 1.0 the attack never ends. Common fix: aim *past* the peak (say 1.2) and switch to decay when the level crosses 1.0.
2. **Release:** the level gets ever smaller without reaching 0. Stop at a threshold (e.g. 1e-5, which is −100 dB) and mark the voice idle so the voice allocator can reuse it. Very tiny floating-point values (subnormals) can also be slow on some processors.

```python
import math

def coef(tau, fs):
    return 1.0 - math.exp(-1.0 / (tau * fs))

class ExpADSR:
    """a, d, r are time constants (s)."""
    def __init__(self, fs, a, d, s, r):
        self.ca = coef(a, fs)
        self.cd = coef(d, fs)
        self.cr = coef(r, fs)
        self.s = s
        self.stage, self.y = "idle", 0.0

    def _toward(self, c, target):
        self.y += c * (target - self.y)

    def gate(self, on):
        if on:
            self.stage = "attack"
        else:
            self.stage = "release"

    def next(self):
        st = self.stage
        if st == "attack":
            # aim past 1.0 so we arrive
            self._toward(self.ca, 1.2)
            if self.y >= 1.0:
                self.y = 1.0
                self.stage = "decay"
        elif st == "decay":
            self._toward(self.cd, self.s)
        elif st == "release":
            self._toward(self.cr, 0.0)
            if self.y < 1e-5:      # -100 dB
                self.y = 0.0
                self.stage = "idle"
        return self.y

fs = 48000
env = ExpADSR(fs, a=0.005, d=0.1,
              s=0.6, r=0.2)
env.gate(True)
n = 0
while env.stage == "attack":
    env.next()
    n += 1
print("attack ms:", round(n / fs * 1000, 2))
for _ in range(fs):                # 1 s
    env.next()
print("level:", round(env.y, 4))
env.gate(False)
n = 0
while env.stage != "idle":
    env.next()
    n += 1
print("release ms:", round(n / fs * 1000))
```

```
attack ms: 8.98
level: 0.6
release ms: 2200
```

Notice the numbers. Both follow from one rule: the time an exponential segment takes depends only on how many times smaller the remaining distance must get.

```formula
t = τ × ln(d_start / d_end)
t_a = 5 ms × ln(1.2 / 0.2) = 5 ms × ln(6)
t_a ≈ 5 ms × 1.79 ≈ 9 ms
t_r = 0.2 s × ln(0.6 / 0.00001)
t_r ≈ 0.2 s × 11.0 ≈ 2.2 s
where
t: the time the segment takes, in seconds (s) or milliseconds (ms)
τ: tau, the segment's time constant
ln: the natural logarithm (inverse of the exponential function)
d_start: the distance to the target when the segment starts
d_end: the distance to the target when the segment stops
t_a: the attack time: aiming at 1.2 from 0, the distance shrinks from 1.2 to 0.2 when the level reaches 1.0
t_r: the release time: aiming at 0 from 0.6, it stops at the 0.00001 (−100 dB) threshold
ms: milliseconds, thousandths of a second
s: seconds
≈: approximately equal to
In words: the time depends on the ratio of the start and end distances, not on their size, so a release that must fall a long way in decibels lasts many time constants.
```

So with a 5 ms time constant and a 1.2 target, the attack takes about 9 ms, and a 200 ms release time constant takes 2.2 s to fall from 0.6 to −100 dB. **"Release = 200 ms" is ambiguous** unless you say what it means: time constant, time to −60 dB, or time to silence. Pick a definition, document it, and convert the knob value to a coefficient accordingly.

## Retriggering and clicks

A **click** is the sound of a discontinuity: the waveform or its gain jumps between two samples. Envelopes cause clicks in a few classic ways:

- **Hard reset on retrigger.** A note is releasing at level 0.4 and you press another key on the same voice. If the envelope jumps to 0 before attacking, the output gain drops 0.4 in one sample. Instead, start the attack **from the current level**, as the code above does.
- **Zero-length attack or release.** A gain jump from 0 to 1 on a waveform that isn't at a zero crossing is a step. Enforce a minimum of around a millisecond or two (a rule of thumb, not a standard).
- **Voice stealing.** Reassigning a sounding voice to a new note jumps both its pitch and its envelope. Fade it out quickly first.
- **Phase reset.** Resetting the oscillator phase on a voice that is still audible is also a step.

Some percussive patches *want* a click (a sharp attack). The point is to choose it, not suffer it.

## Legato and trigger modes

On a mono synth, what happens when you press a new key while still holding the old one?

- **Multi-trigger:** every new note retriggers the envelopes. Each note is articulated.
- **Single-trigger (legato):** if a key is already held, the new note changes pitch only; the envelopes carry on from where they are. Only a fresh press after all keys are up retriggers.

Legato is often paired with **glide** (portamento): the pitch slides to the new note, typically smoothed in the log-frequency (semitone) domain so equal times cover equal musical intervals.

## Parameter smoothing and zipper noise

Controls arrive in steps:

- A MIDI CC has 128 values. Sweeping cutoff or volume with it moves in 127 audible steps.
- A knob read by an ADC is noisy and quantised.
- Control values often update once per audio block. At 48 kHz with 32-sample blocks, that's a staircase changing 1,500 times a second.

Each step in gain or cutoff is a small discontinuity. A sequence of them sounds like a rasping buzz while the knob moves: **zipper noise**. The fix is to let the control set a *target* and move the actual parameter towards it smoothly, every sample.

```python
import math

class OnePoleSmoother:
    def __init__(self, tau, fs, value=0.0):
        self.c = 1.0 - math.exp(
            -1.0 / (tau * fs))
        self.y = self.target = value

    def set(self, target):    # control side
        self.target = target

    def next(self):           # every sample
        y, t = self.y, self.target
        self.y = y + self.c * (t - y)
        return self.y

class LinearRamp:
    def __init__(self, n, value=0.0):
        self.n = n               # samples
        self.y = value
        self.left, self.step = 0, 0.0

    def set(self, target):
        d = target - self.y
        self.step = d / self.n
        self.left = self.n

    def next(self):
        if self.left > 0:
            self.y += self.step
            self.left -= 1
        return self.y

fs = 48000
a = OnePoleSmoother(0.005, fs)   # tau 5 ms
b = LinearRamp(240)              # 5 ms
a.set(1.0)
b.set(1.0)
ya = [a.next() for _ in range(480)]
yb = [b.next() for _ in range(480)]
print(round(ya[239], 3), round(ya[479], 3))
print(round(yb[239], 3), round(yb[479], 3))
```

```
0.632 0.865
1.0 1.0
```

The printed values check out against the formulas. After 240 samples (5 ms, one time constant) the one-pole has covered 63.2% of the way; after 480 samples (two time constants) 86.5%. The linear ramp's step is the distance divided by its length:

```formula
Δy = (g − y_0) / N
Δy = (1.0 − 0) / 240 ≈ 0.00417
where
Δy: delta y, the change per sample
g: the target value, here 1.0
y_0: the value when the ramp starts, here 0
N: the ramp length, in samples; 240 samples is 5 ms at 48 kHz
≈: approximately equal to
In words: the ramp covers the whole distance in exactly N equal steps, then stops.
```

The one-pole smoother is the simplest option: one multiply-add per sample, no state beyond the current value, and it handles a target that keeps moving gracefully. The linear ramp arrives *exactly* after N samples, which is useful when you need a guaranteed time (e.g. a voice-steal fade before reuse) but needs recalculating whenever the target changes.

### Choosing smoothing times

There's no universal value; listen and measure. Useful starting points:

- **Gain and mix levels:** a few milliseconds to a few tens of milliseconds. Too short and zipper noise returns; too long and the control feels laggy.
- **Filter cutoff:** similar, and smooth it in a perceptual unit (octaves) rather than hertz so sweeps sound even.
- **Pitch:** small smoothing for knob jitter; deliberate glide is a separate musical control.
- **Noisy ADC knobs:** combine smoothing with a small dead-band or hysteresis so a stationary knob doesn't wobble the parameter.

Smoothing in the right domain matters. Gain heard in decibels, and frequency heard in octaves, are perceptually logarithmic. Smoothing a frequency linearly from 100 Hz to 10 kHz spends most of its time in the top octaves:

```formula
O = log_2(f_2 / f_1)
O = log_2(10000 Hz / 100 Hz) ≈ 6.64
r_1 = (200 − 100) / (10000 − 100) ≈ 0.01
where
O: the number of octaves between two frequencies
log_2: the base-2 logarithm: how many doublings get from one number to the other
f_1, f_2: the start and end frequencies, in hertz (Hz)
r_1: the share of a linear-in-hertz sweep's time spent in the first octave, 100 to 200 Hz
Hz: hertz, per second
≈: approximately equal to
In words: the sweep covers about 6.6 octaves, but a straight line in hertz spends only about 1% of its time in the first one and about half in the last.
```

A sweep that is linear in octaves instead gives each octave an equal share of the time, which sounds even. JUCE's `SmoothedValue`, for example, offers both linear and multiplicative smoothing for this reason.

> [!note] Where this fits on hardware
> On a microcontroller, the main loop or a timer reads knobs and MIDI and writes *targets*; the audio callback runs the smoothers per sample. That split keeps slow, irregular work out of the audio path. Embedded lessons later cover how to pass those values safely.

## Key takeaways

- ADSR: attack, decay and release are times; sustain is a level held while the gate is on.
- One-pole segments (`y += c * (target - y)`) give analogue-like exponential curves; aim past the peak in the attack and stop the release at a threshold.
- Define what a "time" control means (time constant, to −60 dB, to silence); the difference can be 10× or more.
- Clicks are discontinuities: retrigger from the current level, avoid zero-length segments, fade stolen voices.
- Smooth every audible parameter per sample to avoid zipper noise; choose times by ear, and smooth in log units for pitch, cutoff and gain where appropriate.

## Further reading

- [Envelope (music) — Wikipedia](https://en.wikipedia.org/wiki/Envelope_(music))
- [EarLevel Engineering, Envelope generators](https://www.earlevel.com/main/2013/06/01/envelope-generators/)
- [EarLevel Engineering, Envelope generators: ADSR code](https://www.earlevel.com/main/2013/06/03/envelope-generators-adsr-code/)
- [EarLevel Engineering, A one-pole filter](https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/)
- [JUCE SmoothedValue class reference](https://docs.juce.com/master/classSmoothedValue.html)
- [One-pole filter — Julius O. Smith, Introduction to Digital Filters](https://ccrma.stanford.edu/~jos/filters/One_Pole.html)
