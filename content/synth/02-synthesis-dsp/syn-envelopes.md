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

The simplest implementation moves the level by a fixed step per sample: `step = 1 / (attack_time * fs)` for the attack, and so on. It's easy to reason about, and each segment ends at a precise time.

Linear segments have a drawback for amplitude: hearing is roughly logarithmic, so a linear fade in *amplitude* sounds like it hangs on, then vanishes abruptly at the end. Linear attacks often sound fine; linear releases and decays often sound unnatural.

### Exponential (one-pole) segments

Analogue envelope generators charge and discharge a capacitor through a resistor, which gives exponential curves. Digitally, that is a **one-pole filter** moving towards a target:

```
y += c * (target - y)
c  = 1 - exp(-1 / (tau * fs))
```

`tau` is the **time constant**: after `tau` seconds the level has covered 63.2% of the distance to the target. Measured at 48 kHz with `tau = 10 ms`:

| Fraction reached | Time |
|---|---|
| 63.2% | 10.0 ms |
| 99% | 46.1 ms (4.6 τ) |
| 99.9% | 69.1 ms (6.9 τ) |

An exponential approach never quite arrives, which creates two practical issues:

1. **Attack:** if the target is 1.0 the attack never ends. Common fix: aim *past* the peak (say 1.2) and switch to decay when the level crosses 1.0.
2. **Release:** the level gets ever smaller without reaching 0. Stop at a threshold (e.g. 1e-5, which is −100 dB) and mark the voice idle so the allocator can reuse it. Very tiny floating-point values (subnormals) can also be slow on some processors.

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

Notice the numbers. With a 5 ms time constant and a 1.2 target, the attack takes `5 × ln(6) ≈ 9 ms`. A 200 ms release time constant takes 2.2 s to fall from 0.6 to −100 dB. **"Release = 200 ms" is ambiguous** unless you say what it means: time constant, time to −60 dB, or time to silence. Pick a definition, document it, and convert the knob value to a coefficient accordingly.

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

The one-pole smoother is the simplest option: one multiply-add per sample, no state beyond the current value, and it handles a target that keeps moving gracefully. The linear ramp arrives *exactly* after N samples, which is useful when you need a guaranteed time (e.g. a voice-steal fade before reuse) but needs recalculating whenever the target changes.

### Choosing smoothing times

There's no universal value; listen and measure. Useful starting points:

- **Gain and mix levels:** a few milliseconds to a few tens of milliseconds. Too short and zipper noise returns; too long and the control feels laggy.
- **Filter cutoff:** similar, and smooth it in a perceptual unit (octaves) rather than hertz so sweeps sound even.
- **Pitch:** small smoothing for knob jitter; deliberate glide is a separate musical control.
- **Noisy ADC knobs:** combine smoothing with a small dead-band or hysteresis so a stationary knob doesn't wobble the parameter.

Smoothing in the right domain matters. Gain heard in decibels, and frequency heard in octaves, are perceptually logarithmic. Smoothing a frequency linearly from 100 Hz to 10 kHz spends most of its time in the top octaves. JUCE's `SmoothedValue`, for example, offers both linear and multiplicative smoothing for this reason.

> [!note] Where this fits on hardware
> On a microcontroller, the main loop or a timer reads knobs and MIDI and writes *targets*; the audio callback runs the smoothers per sample. That split keeps slow, irregular work out of the audio path. Embedded lessons later cover how to pass those values safely.

## Key takeaways

- ADSR: attack, decay and release are times; sustain is a level held while the gate is on.
- One-pole segments (`y += c·(target − y)`) give analogue-like exponential curves; aim past the peak in the attack and stop the release at a threshold.
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
