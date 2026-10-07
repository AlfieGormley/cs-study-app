---
id: syn-filters
title: Filters
level: intermediate
minutes: 15
summary: Frequency response, cutoff, slope, resonance and Q; the one-pole low-pass in full (difference equation, coefficient, state, measured response, stability); IIR versus FIR; and a conceptual tour of the biquad, state-variable and ladder filters used in synths.
---

In a subtractive synth the filter is where most of the character lives. The oscillator supplies a bright, buzzy spectrum; the filter decides how much of it you hear, and sweeping the filter is what makes a sound "open up" or "wow".

This lesson builds one filter fully (the one-pole low-pass) and introduces the resonant designs you'll use from a library, so you can choose and drive them sensibly.

## Frequency response

A linear time-invariant filter, after startup transients settle, treats each sine component separately: a sine goes in, a sine at the **same frequency** comes out, scaled in amplitude and shifted in phase. The **frequency response** says how much, for every frequency.

- **Magnitude response:** gain versus frequency, usually in dB on a log-frequency axis.
- **Phase response:** the time shift versus frequency.

Filter types by shape:

| Type | Passes | Removes |
|---|---|---|
| Low-pass (LP) | below cutoff | above cutoff |
| High-pass (HP) | above cutoff | below cutoff |
| Band-pass (BP) | around cutoff | both sides |
| Notch | both sides | around cutoff |

## Cutoff, slope and order

The **cutoff** frequency is where the filter starts to act; for simple low-pass filters it's usually defined as the −3 dB point (half power).

Above cutoff, a low-pass filter's gain falls at a **slope** set by its **order** (number of poles). Each pole contributes about 6 dB per octave:

| Order | Slope | Common name |
|---|---|---|
| 1 | 6 dB/oct | one-pole |
| 2 | 12 dB/oct | two-pole, biquad |
| 4 | 24 dB/oct | four-pole, ladder |

Steeper slopes sound more "synthy" and decisive; gentle slopes sound more natural.

## Resonance and Q

A resonant filter boosts frequencies **near the cutoff** before rolling off. On a synth this is the **resonance** (or emphasis) control. Turn it up and the filter "sings" at the cutoff frequency; sweep it and you hear the classic wah.

**Q** (quality factor) measures that peakiness for a two-pole filter. Q = 0.7071 (1/√2) is the Butterworth value: maximally flat, no peak, −3 dB at cutoff. Higher Q means a taller, narrower peak. For the RBJ cookbook low-pass, the gain at the cutoff frequency equals Q, as a numerical check at fs = 48 kHz, f0 = 1 kHz confirms:

| Q | Gain at f0 |
|---|---|
| 0.7071 | −3.0 dB |
| 2 | +6.0 dB |
| 4 | +12.0 dB |
| 10 | +20.0 dB |

At high enough resonance, some filters **self-oscillate**: the peak becomes so strong that the filter rings at its cutoff with no input, effectively becoming a sine oscillator. Analogue players use this deliberately.

## The one-pole low-pass

The simplest useful filter. Its **difference equation** says how each output sample is computed:

```
y[n] = y[n-1] + a * (x[n] - y[n-1])
     = a * x[n] + (1 - a) * y[n-1]
```

Each output moves a fraction `a` of the way from the previous output towards the new input. It's the same formula as the envelope and smoother in the last lesson, now running on audio. Small `a` means heavy smoothing (low cutoff).

The coefficient from a cutoff `fc` (one standard choice, also used by EarLevel Engineering):

```
a = 1 - exp(-2π * fc / fs)
```

The **state** is the single number `y[n-1]`. It must persist across samples and blocks, exactly like oscillator phase, and each voice needs its own.

```python
import math

class OnePoleLP:
    def __init__(self, fc, fs):
        w = 2 * math.pi * fc / fs
        self.a = 1.0 - math.exp(-w)
        self.y = 0.0       # the state

    def process(self, x):
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
    db = 20 * math.log10(peak)
    print(f, round(db, 1))
```

```
100 -0.0
1000 -3.0
4000 -12.2
16000 -22.5
```

This is the roadmap exercise "measure its effect at selected frequencies": feed in sines and measure what comes out. The theoretical response `|H| = a / |1 − (1 − a)e^(−jω)|` gives these values to the displayed precision, and filling in more points gives the table below. Measuring only the largest sample is generally phase-dependent; for more accurate sine amplitude estimates, fit sine/cosine coefficients or measure RMS over complete cycles.

| Input | Gain (fc = 1 kHz) |
|---|---|
| 500 Hz | −1.0 dB |
| 1 kHz | −3.0 dB |
| 2 kHz | −7.0 dB |
| 4 kHz | −12.2 dB |
| 8 kHz | −17.7 dB |
| 16 kHz | −22.5 dB |

The slope settles towards about 6 dB per octave above cutoff, then flattens as it approaches Nyquist (the digital filter is not an exact copy of an analogue one up there).

> [!warning] Cutoff accuracy at high frequencies
> The `exp` formula puts the −3 dB point very close to `fc` when `fc` is well below Nyquist. Measured at 48 kHz: fc = 1 kHz gives −3 dB at about 1,002 Hz, but fc = 5 kHz gives about 5,190 Hz, fc = 10 kHz about 11.9 kHz, and fc = 15 kHz never reaches −3 dB below Nyquist. If you need accurate high cutoffs, use a design based on the bilinear transform with prewarping (as the RBJ cookbook does).

The same structure gives a **one-pole high-pass** for free: `hp = x − lp(x)`. With a very low cutoff (a few hertz) that is a **DC blocker**, handy for removing the offset from a pulse wave.

## IIR and FIR

The one-pole filter feeds its own output back (`y[n-1]`). Its impulse response (the output when you feed in a single 1 followed by zeros) is `a, a(1−a), a(1−a)², ...`, decaying for ever. That makes it an **infinite impulse response (IIR)** filter.

A **finite impulse response (FIR)** filter uses only current and past *inputs*:

```
y[n] = b0*x[n] + b1*x[n-1] + ... + bN*x[n-N]
```

| | IIR | FIR |
|---|---|---|
| Feedback | yes | no |
| Cost for a steep slope | low | high (many taps) |
| Always stable | no | yes |
| Linear phase possible | no | yes |

Synth filters are almost always IIR: cheap, easy to sweep, and their resonance comes from feedback. FIR filters show up in oversampling and decimation, where linear phase and guaranteed stability matter.

## Stability, intuitively

Feedback can run away. If the fraction fed back is too large, every sample adds more than the last and the output grows without limit.

For the one-pole, the feedback multiplier is `(1 − a)`. The filter is stable if `|1 − a| < 1`, i.e. `0 < a < 2`. The `exp` formula always gives `0 < a < 1`, so it is always stable. But a common shortcut, `a = 2π·fc/fs`, exceeds 2 when `fc > fs/π` (about 15.3 kHz at 48 kHz). Sweep the cutoff up there and the filter blows up.

In general a digital IIR filter is stable when all its **poles** lie inside the unit circle. You don't need the theory yet; you need the habits:

- Clamp cutoff and resonance to the range the design supports.
- Compute coefficients with the design's own formulas, not approximations.
- Watch for NaN or infinity in the output during development, and reset the filter state if it appears.

## Resonant filter designs (conceptual)

You aren't expected to implement these yet. Know what they are, so you can pick one from a library and drive it well.

### Biquad (RBJ cookbook)

A general second-order IIR section, five coefficients:

```
y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2]
               - a1*y[n-1] - a2*y[n-2]
```

Robert Bristow-Johnson's **Audio EQ Cookbook** (now a W3C note) gives formulas for low-pass, high-pass, band-pass, notch, peaking and shelving filters from `f0`, `Q` (or bandwidth) and gain. It's the standard choice for EQs. The cookbook's second-order low/high-pass responses approach 12 dB/oct in their analogue-style stopband region; two cascaded stages give 24 dB/oct. Notch, peaking and shelving biquads do not share that blanket slope rule.

Caveat: the common direct-form structures are known to behave poorly when coefficients change rapidly (fast cutoff sweeps): Wishnick (DAFx 2014) documents clicks when Direct Form II coefficients change, and a time-varying recursive filter can go unstable even when every individual coefficient set is stable. That's why synth filters often use other structures.

### State-variable filter (SVF)

A two-integrator loop that produces low-pass, band-pass and high-pass outputs at once, with cutoff and resonance controls that are nearly independent. The classic digital version (Chamberlin's) is very cheap but misbehaves at high cutoffs: its tuning drifts and, especially at low resonance, it goes unstable once the cutoff rises past roughly fs/7 to fs/6 (about 6.5 to 8.3 kHz at 48 kHz for Q between 0.5 and 0.707), so it is often run oversampled. Modern versions based on trapezoidal integration, such as Andrew Simper's (Cytomic), stay well-behaved when modulated quickly: Simper's paper states the filter remains stable and smooth even with audio-rate modulation, and Wishnick gives a proof of the SVF's stable time-varying behaviour. That is what synths need.

### Ladder

Robert Moog's patented transistor ladder: four one-pole low-pass stages in series (24 dB/oct) with negative feedback from the output to the input. Stilson and Smith's analysis models the feedback gain `k` from 0 to 4: as `k` approaches 4 the gain at cutoff goes to infinity and the filter self-oscillates. Two well-known traits follow from the model: resonance comes with a drop in low-frequency level (DC gain is `1/(1 + k)`), and the feedback loop has no delay, so digital versions need care (a unit delay in the loop, or an implicit/zero-delay-feedback solution).

```diagram
x -->(+)--[LP]--[LP]--[LP]--[LP]--+--> y
      ^                           |
      |                           |
      +----------(-k)-------------+
```

> [!tip] Drive cutoff in octaves
> Pitch, envelope and LFO modulation of cutoff should add in octaves (log frequency), then convert: `fc = base * 2 ** octaves`. Clamp the result to a safe range (e.g. 20 Hz up to somewhat below Nyquist) before computing coefficients.

## Key takeaways

- A filter scales and phase-shifts each sine; its frequency response shows how much at each frequency.
- Each pole adds about 6 dB/oct of slope; resonance (Q) adds a peak at cutoff, and gain at f0 equals Q for the RBJ low-pass.
- One-pole low-pass: `y += a·(x − y)`, `a = 1 − exp(−2π·fc/fs)`, one state value per voice; measured −3 dB at 1 kHz and −12.2 dB at 4 kHz for fc = 1 kHz.
- IIR filters use feedback (cheap, can be unstable); FIR filters don't (stable, costlier).
- Biquad, SVF and ladder are the common resonant designs; prefer structures that tolerate fast modulation, and clamp parameters.

## Further reading

- [Introduction to Digital Filters — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
- [One-pole filter — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/One_Pole.html)
- [EarLevel Engineering, A one-pole filter](https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/)
- [Audio EQ Cookbook (RBJ) — W3C](https://www.w3.org/TR/audio-eq-cookbook/)
- [Andrew Simper, Linear trapezoidal integrated SVF (PDF)](https://cytomic.com/files/dsp/SvfLinearTrapOptimised2.pdf)
- [Wishnick, Time-Varying Filters for Musical Applications (DAFx 2014, PDF)](https://www.dafx14.fau.de/papers/dafx14_aaron_wishnick_time_varying_filters_for_.pdf)
- [Stilson and Smith, Analyzing the Moog VCF (PDF)](https://ccrma.stanford.edu/~stilti/papers/moogvcf.pdf)
- [Infinite impulse response — Wikipedia](https://en.wikipedia.org/wiki/Infinite_impulse_response)
- [Butterworth filter — Wikipedia](https://en.wikipedia.org/wiki/Butterworth_filter)
