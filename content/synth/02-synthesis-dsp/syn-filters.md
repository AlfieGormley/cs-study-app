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

To estimate how much a low-pass cuts a frequency well above its cutoff, count the octaves and multiply by the slope:

```formula
S ≈ 6 dB/oct × N_p
A ≈ S × log_2(f / f_c)
A ≈ 24 dB/oct × log_2(4000 Hz / 500 Hz)
A ≈ 24 dB/oct × 3 = 72 dB
where
S: the slope well above cutoff, in decibels per octave (dB/oct)
N_p: the filter's order: its number of poles
A: the attenuation at frequency f: how much quieter the output is than the input, in decibels (dB)
log_2: the base-2 logarithm: the number of doublings (octaves) from f_c up to f
f: the frequency you are asking about, in hertz (Hz)
f_c: the cutoff frequency, in Hz
dB: decibels
oct: octave, a doubling of frequency
Hz: hertz, cycles per second
≈: approximately equal to
In words: each pole adds about 6 dB of cut per octave, and the total cut is the slope times the number of octaves above cutoff; a four-pole filter at 500 Hz cuts a 4 kHz harmonic by about 72 dB.
```

This is an asymptote (the straight line the curve approaches): near the cutoff, and with resonance, the real curve differs, so use it only for frequencies well above cutoff.

Steeper slopes sound more "synthy" and decisive; gentle slopes sound more natural.

## Resonance and Q

A resonant filter boosts frequencies **near the cutoff** before rolling off. On a synth this is the **resonance** (or emphasis) control. Turn it up and the filter "sings" at the cutoff frequency; sweep it and you hear the classic wah.

**Q** (quality factor) measures that peakiness for a two-pole filter. A Q of about 0.7071 (one divided by the square root of 2) is the **Butterworth** value: maximally flat, no peak, −3 dB at cutoff. Higher Q means a taller, narrower peak. For the RBJ cookbook low-pass, the gain at the cutoff frequency equals Q:

```formula
G(f_0) = Q
G_dB = 20 × log_10(Q)
G_dB = 20 × log_10(4) ≈ +12.0 dB
G_dB = 20 × log_10(0.7071) ≈ −3.0 dB
where
G(f_0): the filter's gain (output amplitude divided by input amplitude) at its cutoff frequency
f_0: the cutoff frequency, the cookbook's name for it, in hertz
Q: the quality factor, a plain number with no unit; higher means a taller, narrower peak
G_dB: the same gain in decibels (dB)
log_10: the base-10 logarithm: the power you raise 10 to to get the number
dB: decibels
≈: approximately equal to
In words: at the cutoff the RBJ low-pass multiplies the signal by Q, so Q = 4 is a 12 dB boost and Q = 0.7071 is a 3 dB cut.
```

A numerical check at a 48 kHz sample rate with a 1 kHz cutoff confirms it:

| Q | Gain at f0 |
|---|---|
| 0.7071 | −3.0 dB |
| 2 | +6.0 dB |
| 4 | +12.0 dB |
| 10 | +20.0 dB |

At high enough resonance, some filters **self-oscillate**: the peak becomes so strong that the filter rings at its cutoff with no input, effectively becoming a sine oscillator. Analogue players use this deliberately.

## The one-pole low-pass

The simplest useful filter. Its **difference equation** says how each output sample is computed:

```formula
y[n] = y[n−1] + a × (x[n] − y[n−1])
y[n] = a × x[n] + (1 − a) × y[n−1]
where
x[n]: the input sample at step n
y[n]: the output sample at step n; y[n−1] is the previous output
n: the sample index (0, 1, 2...); [n−1] means one sample earlier
a: the filter coefficient, between 0 and 1; small a means heavy smoothing (a low cutoff)
In words: each output moves a fraction a of the way from the previous output towards the new input; the second line is the same rule rearranged as a weighted average of the new input and the old output.
```

It's the same formula as the envelope and smoother in the last lesson, now running on audio. For example, with a = 0.1227, starting from 0, a step input (x jumps from 0 to 1 and stays there) gives outputs of 0.1227, 0.230, 0.325...: an exponential rise towards 1.

The coefficient comes from the cutoff (one standard choice, also used by EarLevel Engineering):

```formula
a = 1 − exp(−2π × f_c / f_s)
a = 1 − exp(−2π × 1000 / 48000)
a = 1 − exp(−0.1309) ≈ 0.1227
where
a: the one-pole coefficient
exp: the exponential function, e (about 2.71828) raised to a power
π: pi, about 3.14159
f_c: the cutoff frequency, in hertz (Hz), here 1 kHz
f_s: the sample rate, in Hz, here 48,000
≈: approximately equal to
In words: the coefficient depends on the cutoff as a fraction of the sample rate; a higher cutoff gives a bigger a (less smoothing), and a always stays between 0 and 1.
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

This is the roadmap exercise "measure its effect at selected frequencies": feed in sines and measure what comes out. Theory gives the same answers. The filter's magnitude response is:

```formula
|H| = a / |1 − (1 − a) × e^{−j × ω}|
ω = 2π × f / f_s
where
|H|: the filter's gain at frequency f (output amplitude divided by input amplitude); 20 × log_10 of it gives decibels
a: the coefficient, here 0.1227
e^{−j × ω}: a complex number of size 1 at angle −ω; it stands for a one-sample delay at this frequency
e: Euler's number, about 2.71828
j: the imaginary unit, the square root of −1 (engineers write j rather than i)
ω: omega, the frequency as an angle per sample, in radians per sample
π: pi, about 3.14159
f: the input frequency, in hertz (Hz)
f_s: the sample rate, in Hz
|x|: the magnitude (size) of a number, ignoring its sign or angle
In words: the gain is a divided by the size of a complex number that grows with frequency, so higher frequencies come out quieter; at 1 kHz with a = 0.1227 it is about 0.708, which is −3.0 dB.
```

It gives the measured values to the displayed precision, and filling in more points gives the table below. Measuring only the largest sample is generally phase-dependent; for more accurate sine amplitude estimates, fit sine/cosine coefficients or measure RMS over complete cycles.

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
> The `exp` formula puts the −3 dB point very close to the set cutoff when the cutoff is well below Nyquist. Measured at 48 kHz: a 1 kHz setting gives −3 dB at about 1,002 Hz, but 5 kHz gives about 5,190 Hz, 10 kHz about 11.9 kHz, and a 15 kHz setting never reaches −3 dB below Nyquist. If you need accurate high cutoffs, use a design based on the bilinear transform with prewarping (as the RBJ cookbook does).

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

## IIR and FIR

The one-pole filter feeds its own output back (the previous output). Its **impulse response** (the output when you feed in a single 1 followed by zeros) is:

```formula
h[n] = a × (1 − a)^{n}
h[0] = 0.1227, h[1] ≈ 0.1076, h[2] ≈ 0.0944
where
h[n]: the impulse response: the output n samples after a single 1 was fed in
a: the coefficient, here 0.1227
n: the number of samples since the impulse
≈: approximately equal to
In words: each sample the output shrinks by the factor 1 − a, so it decays for ever without ever quite reaching zero.
```

That makes it an **infinite impulse response (IIR)** filter.

A **finite impulse response (FIR)** filter uses only current and past *inputs*:

```formula
y[n] = b_0 × x[n] + b_1 × x[n−1]
     + … + b_N × x[n−N]
where
y[n]: the output at sample n
x[n]: the input at sample n; x[n−1] is one sample earlier and x[n−N] is N samples earlier
b_0, b_1, b_N: the filter's coefficients (its **taps**), fixed numbers chosen by the design
N: the filter's order: how many past inputs it uses
…: and so on: one term for every delay in between
In words: each output is a weighted sum of the current input and the last N inputs, with no feedback, so an impulse passes through in N + 1 samples and is gone.
```

For example, b_0 = b_1 = b_2 = 1/3 (with N = 2) is a three-sample moving average, a gentle low-pass.

| | IIR | FIR |
|---|---|---|
| Feedback | yes | no |
| Cost for a steep slope | low | high (many taps) |
| Always stable | no | yes |
| Linear phase possible | no | yes |

Synth filters are almost always IIR: cheap, easy to sweep, and their resonance comes from feedback. FIR filters show up in oversampling and decimation, where linear phase and guaranteed stability matter.

## Stability, intuitively

Feedback can run away. If the fraction fed back is too large, every sample adds more than the last and the output grows without limit.

For the one-pole, the previous output is multiplied by 1 − a every sample. If that multiplier's size reaches 1 or more, the output never dies away:

```formula
|1 − a| < 1
0 < a < 2
a_sc = 2π × f_c / f_s
f_max = f_s / π
f_max = 48000 Hz / 3.14159 ≈ 15279 Hz
where
|x|: absolute value: x without its sign
a: the one-pole coefficient; the filter is stable only for values strictly between 0 and 2
<: less than
a_sc: the coefficient given by a common shortcut formula
π: pi, about 3.14159
f_c: the cutoff, in hertz (Hz)
f_s: the sample rate, in Hz
f_max: the cutoff at which the shortcut's coefficient reaches 2; above it the filter is unstable
Hz: hertz
≈: approximately equal to
In words: the filter is stable while the feedback multiplier 1 − a stays between −1 and 1; the exp formula always keeps a between 0 and 1, but the shortcut passes 2 once the cutoff exceeds the sample rate divided by π.
```

So the exp formula is always stable, but with the shortcut, sweeping the cutoff above about 15.3 kHz at 48 kHz makes the filter blow up.

In general a digital IIR filter is stable when all its **poles** lie inside the unit circle. You don't need the theory yet; you need the habits:

- Clamp cutoff and resonance to the range the design supports.
- Compute coefficients with the design's own formulas, not approximations.
- Watch for NaN or infinity in the output during development, and reset the filter state if it appears.

## Resonant filter designs (conceptual)

You aren't expected to implement these yet. Know what they are, so you can pick one from a library and drive it well.

### Biquad (RBJ cookbook)

A general second-order IIR section, five coefficients:

```formula
y[n] = b_0 × x[n] + b_1 × x[n−1]
     + b_2 × x[n−2]
     − a_1 × y[n−1] − a_2 × y[n−2]
where
y[n]: the output at sample n; y[n−1] and y[n−2] are the two previous outputs
x[n]: the input at sample n; x[n−1] and x[n−2] are the two previous inputs
n: the sample index
b_0, b_1, b_2: the feedforward coefficients, which act on inputs
a_1, a_2: the feedback coefficients, which act on past outputs (the cookbook divides every coefficient by a sixth one, a_0, so it does not appear)
In words: each output mixes the current and two previous inputs, minus a mix of the two previous outputs; the five numbers set the filter's type, cutoff and Q.
```

Robert Bristow-Johnson's **Audio EQ Cookbook** (now a W3C note) gives formulas for low-pass, high-pass, band-pass, notch, peaking and shelving filters from a centre or cutoff frequency (`f0`), `Q` (or the width of the band) and gain. It's the standard choice for EQs. The cookbook's second-order low/high-pass responses approach 12 dB/oct in their analogue-style stopband region; two cascaded stages give 24 dB/oct. Notch, peaking and shelving biquads do not share that blanket slope rule.

Caveat: the common direct-form structures are known to behave poorly when coefficients change rapidly (fast cutoff sweeps): Wishnick (DAFx 2014) documents clicks when Direct Form II coefficients change, and a time-varying filter with feedback (IIR) can go unstable even when every individual coefficient set is stable. That's why synth filters often use other structures.

### State-variable filter (SVF)

A two-integrator loop that produces low-pass, band-pass and high-pass outputs at once, with cutoff and resonance controls that are nearly independent. The classic digital version (Chamberlin's) is very cheap but misbehaves at high cutoffs: its tuning drifts and, especially at low resonance, it goes unstable once the cutoff rises past roughly a seventh to a sixth of the sample rate (about 6.5 to 8.3 kHz at 48 kHz for Q between 0.5 and 0.707), so it is often run oversampled. Modern versions based on trapezoidal integration, such as Andrew Simper's (Cytomic), stay well-behaved when modulated quickly: Simper's paper states the filter remains stable and smooth even with audio-rate modulation, and Wishnick gives a proof of the SVF's stable time-varying behaviour. That is what synths need.

### Ladder

Robert Moog's patented transistor ladder: four one-pole low-pass stages in series (24 dB/oct) with negative feedback from the output to the input. Stilson and Smith's analysis models the feedback gain `k` from 0 to 4: as `k` approaches 4 the gain at cutoff goes to infinity and the filter self-oscillates. Two well-known traits follow from the model: resonance comes with a drop in low-frequency level (worked out below), and the feedback loop has no delay, so digital versions need care (a unit delay in the loop, or an implicit/zero-delay-feedback solution).

```diagram
x -->(+)--[LP]--[LP]--[LP]--[LP]--+--> y
      ^                           |
      |                           |
      +----------(-k)-------------+
```

The model's response shows where the bass loss comes from:

```formula
H(s) = 1 / (k + (1 + s / ω_c)^4)
H(0) = 1 / (k + 1)
G_0 = 20 × log_10(1 / (3 + 1)) ≈ −12 dB
where
H(s): the filter's transfer function: its gain and phase shift at complex frequency s
s: the Laplace variable (complex frequency); for a steady sine of angular frequency ω, s = j × ω, where j is the imaginary unit (the square root of −1), so s = 0 means DC (0 Hz)
ω_c: omega c, the cutoff as an angular frequency, in radians per second (2π times the cutoff in hertz)
k: the resonance feedback gain, from 0 (none) to 4 (self-oscillation)
H(0): the gain at DC, i.e. the very lowest frequencies
G_0: that DC gain in decibels, for k = 3
log_10: the base-10 logarithm
dB: decibels
≈: approximately equal to
In words: each stage passes DC unchanged (the fourth-power term becomes 1), so the gain there is 1/(k + 1); turning resonance up to k = 3 cuts the bass by about 12 dB.
```

> [!tip] Drive cutoff in octaves
> Pitch, envelope and LFO modulation of cutoff should add in octaves (log frequency), then convert once, as below. Clamp the result to a safe range (e.g. 20 Hz up to somewhat below Nyquist) before computing coefficients.

```formula
f_c = f_base × 2^{o}
f_c = 500 Hz × 2^{1.5} ≈ 1414 Hz
where
f_c: the cutoff actually used, in hertz (Hz)
f_base: the cutoff set by the knob, in Hz
o: the total modulation in octaves (envelope, LFO, key tracking added together), positive or negative
2^{o}: 2 raised to the power o: +1 octave doubles the cutoff, −1 halves it
Hz: hertz
≈: approximately equal to
In words: add up all the modulation in octaves, then convert once by doubling the cutoff for every octave.
```

## Key takeaways

- A filter scales and phase-shifts each sine; its frequency response shows how much at each frequency.
- Each pole adds about 6 dB/oct of slope; resonance (Q) adds a peak at cutoff, and the gain at the cutoff equals Q for the RBJ low-pass.
- One-pole low-pass: `y += a * (x - y)` with `a = 1 - math.exp(-2 * math.pi * fc / fs)`, one state value per voice; measured −3 dB at 1 kHz and −12.2 dB at 4 kHz for a 1 kHz cutoff.
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
