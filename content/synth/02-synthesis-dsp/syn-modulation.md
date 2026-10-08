---
id: syn-modulation
title: Modulation, LFOs and the modulation matrix
level: advanced
minutes: 15
summary: LFO rates, shapes and bipolar or unipolar ranges; vibrato and tremolo with correct depth units; envelope and velocity modulation of the filter; a modulation matrix; and the trade-offs of control-rate versus audio-rate modulation.
---

A static patch sounds lifeless. **Modulation** means letting one signal change a parameter of another over time: an LFO wobbling pitch, an envelope sweeping cutoff, key velocity opening the filter. Most of a synth's expressiveness comes from what modulates what, and by how much.

This lesson covers the sources, how to scale and combine them in the right units, and where to compute them.

## LFOs

A **low-frequency oscillator** is the same phase accumulator as an audio oscillator, run below the audible pitch range. Typical rates run from well under 1 Hz (slow sweeps) to around 20 Hz (fast flutter); there's no fixed standard, and many synths go higher.

Common shapes:

- **Sine / triangle:** smooth, even wobble.
- **Saw / ramp:** repeating rise or fall.
- **Square:** switches between two values (trills).
- **Sample & hold (S&H):** a new random value each cycle, held steady.

Because LFOs only drive controls, aliasing is rarely a concern for them. The sharp edges of a square or S&H LFO can, however, cause **clicks** if applied directly to gain or cutoff, so smooth them a little.

### Bipolar and unipolar

- **Bipolar** sources swing from −1 to +1: the parameter moves both up and down around its setting (vibrato around the note).
- **Unipolar** sources run from 0 to +1: the parameter only moves one way from its setting (tremolo that only *reduces* volume, an envelope that only opens the filter).

Convert a bipolar value to a unipolar one like this:

```formula
u = (b + 1) / 2
u = (−0.5 + 1) / 2 = 0.25
where
u: the unipolar value, from 0 to 1
b: the bipolar value, from −1 to +1
In words: shift the range up by 1 (to 0..2), then halve it (to 0..1); −1 becomes 0, 0 becomes 0.5 and +1 becomes 1.
```

In the code below this is the `unipolar` function.

```python
import math, random

class LFO:
    def __init__(self, rate, update_hz):
        # update_hz: how often next() runs
        # (fs, or fs / block size)
        self.inc = rate / update_hz
        self.p = 0.0
        self.held = 0.0

    def next(self, shape):
        p = self.p
        if shape == "sine":
            v = math.sin(2 * math.pi * p)
        elif shape == "tri":
            v = 1.0 - 4.0 * abs(p - 0.5)
        elif shape == "square":
            v = 1.0 if p < 0.5 else -1.0
        else:               # sample & hold
            v = self.held
        self.p += self.inc
        if self.p >= 1.0:
            self.p -= 1.0
            r = random.uniform(-1, 1)
            self.held = r
        return v                # bipolar

def unipolar(v):
    return 0.5 * (v + 1.0)      # 0..1

fs, block = 48000, 32
lfo = LFO(5.0, fs / block)      # 5 Hz
print(lfo.inc)                  # per block
depth = 0.5                     # tremolo
vals = [lfo.next("sine")
        for _ in range(300)]
gains = [1 - depth * unipolar(v)
         for v in vals]
print(round(min(gains), 3),
      round(max(gains), 3))
```

```
0.0033333333333333335
0.5 1.0
```

The LFO updates once per 32-sample block, so its increment is based on the block rate, not the sample rate:

```formula
f_u = f_s / B = 48000 Hz / 32 = 1500 Hz
inc = r / f_u = 5 Hz / 1500 Hz ≈ 0.00333
g = 1 − d × u
where
f_u: the update rate: how often the LFO's next() runs, in hertz (Hz)
f_s: the sample rate, 48,000 Hz
B: the block size, 32 samples
inc: the LFO's phase increment per update, in cycles
r: the LFO rate, 5 Hz
g: the tremolo gain multiplier
d: the depth, here 0.5
u: the LFO's unipolar value, 0 to 1
Hz: hertz, per second
≈: approximately equal to
In words: the increment is the LFO rate divided by the update rate; with depth 0.5 the gain moves between 1 (when u = 0) and 0.5 (when u = 1).
```

So the LFO updates 1,500 times a second and a 5 Hz cycle takes 300 updates. The tremolo gain swings between 0.5 and 1.0: depth 0.5 means "down to half volume", never above the original.

Two common LFO options:

- **Key sync / retrigger:** reset the LFO phase on each note so every note starts its wobble the same way. Free-running LFOs drift relative to the notes.
- **Tempo sync:** derive the rate from tempo. At 120 BPM a beat lasts 0.5 s, so one cycle per quarter note is 2 Hz.

The tempo-sync conversion in general:

```formula
r = (BPM / 60) / L
r = (120 / 60) / 1 = 2 Hz
r = (90 / 60) / 0.5 = 3 Hz
where
r: the LFO rate, in hertz (Hz): cycles per second
BPM: the tempo in beats per minute; dividing by 60 gives beats per second
L: the length of one LFO cycle, in beats: 1 for a quarter note (one beat in 4/4 time), 0.5 for an eighth note, 4 for a bar of 4/4
Hz: hertz
In words: turn the tempo into beats per second, then divide by how many beats one LFO cycle should last.
```

## Vibrato and tremolo

**Vibrato** is periodic pitch variation; **tremolo** is periodic amplitude variation. (Some instruments and effects use the names loosely; synths use them precisely.)

**Pitch depth belongs in cents or semitones**, because pitch is heard logarithmically. Add the modulation in semitones (or cents), then convert:

```formula
f = f_note × 2^{s/12}
f = f_note × 2^{c/1200}
f = 440 Hz × 2^{50/1200} ≈ 452.89 Hz
where
f: the modulated frequency, in hertz (Hz)
f_note: the note's unmodulated frequency, in Hz
s: the pitch offset in semitones (12 to an octave), positive or negative; for vibrato, the LFO value times the depth in semitones
c: the same offset in cents (100 to a semitone, 1200 to an octave)
2^{x}: 2 raised to the power x: +12 semitones (+1200 cents) doubles f, −12 halves it
Hz: hertz
≈: approximately equal to
In words: add modulation in musical units, then convert by doubling the frequency for every 12 semitones; 50 cents above 440 Hz is about 452.89 Hz.
```

| Vibrato depth | 440 Hz swings between |
|---|---|
| ±50 cents | 427.47 – 452.89 Hz |
| ±100 cents | 415.30 – 466.16 Hz |

A fixed depth in hertz would be wrong: ±10 Hz is a wide vibrato on a bass note and barely noticeable on a high one.

**Gain depth** is usually specified as a fraction of the level (or in dB). Apply it like this:

```formula
g = 1 − d × u
where
g: the gain multiplier applied to the signal
d: the tremolo depth, from 0 (no effect) to 1 (falls to silence)
u: the LFO's unipolar value, from 0 to 1
In words: the gain moves between 1 and 1 − d and never rises above 1.
```

That keeps the peak at the original level and avoids pushing the signal past full scale.

## Envelope, velocity and other sources

The most important modulation in a subtractive synth is the **filter envelope**: a second ADSR, scaled by an *amount*, added to the cutoff. Short attack and decay with low sustain give the classic pluck or "squelch". Like pitch, cutoff should be modulated in **octaves**:

```formula
o = e × A_oct
f_c = f_base × 2^{o}
o = 0.5 × 3 = 1.5
f_c = 500 Hz × 2^{1.5} ≈ 1414 Hz
where
o: the envelope's contribution, in octaves
e: the envelope's current value, from 0 to 1
A_oct: the envelope amount, in octaves: how far the envelope can open the filter
f_c: the cutoff actually used, in hertz (Hz)
f_base: the cutoff set by the knob, in Hz
2^{o}: 2 raised to the power o: each octave doubles the cutoff
Hz: hertz
≈: approximately equal to
In words: scale the envelope by the amount in octaves, then double the base cutoff once per octave; halfway up an envelope with a 3-octave amount, a 500 Hz cutoff opens to about 1,414 Hz.
```

Other standard sources:

- **Velocity:** how hard the key was struck. In MIDI 1.0 it's a 7-bit value (1–127 for a sounding note; a note-on with velocity 0 means note-off). Mapping velocity to both level and cutoff makes harder notes louder *and* brighter, like acoustic instruments.
- **Key tracking:** the note number itself, so the filter opens for higher notes and timbre stays consistent across the keyboard.
- **Mod wheel** (MIDI CC 1), **aftertouch** and **pitch bend:** performance controls, usually scaling vibrato depth or cutoff.
- **Random** per note, for subtle analogue-style variation.

## The modulation matrix

Hard-wiring "LFO → pitch" and "env 2 → cutoff" is fine for a first instrument. A **modulation matrix** generalises it: a list of routes, each with a source, a destination and an amount. Each destination sums its contributions **in its own natural unit**, then converts once.

```python
# sources: current values, already scaled
src = {"env": 0.5,      # unipolar 0..1
       "lfo": -1.0,     # bipolar -1..1
       "vel": 100 / 127}

# (source, destination, amount)
routes = [("env", "cutoff_oct", 3.0),
          ("lfo", "cutoff_oct", 0.5),
          ("vel", "cutoff_oct", 1.0),
          ("lfo", "pitch_semi", 0.25)]

mod = {"cutoff_oct": 0.0, "pitch_semi": 0.0}
for s, d, amt in routes:
    mod[d] += src[s] * amt

base_cut, note_hz = 500.0, 440.0
cut = base_cut * 2 ** mod["cutoff_oct"]
cut = min(max(cut, 20.0), 20000.0)  # clamp
semi = mod["pitch_semi"]
hz = note_hz * 2 ** (semi / 12)
print(round(mod["cutoff_oct"], 3),
      round(cut, 1))
print(round(hz, 2))
```

```
1.787 1726.0
433.69
```

Here the envelope adds 1.5 octaves, the LFO subtracts 0.5 and velocity 100 adds 0.787, for a net +1.787 octaves: 500 Hz becomes 1,726 Hz. As a formula:

```formula
m_d = Σ v_i × k_i
m = 0.5 × 3.0 + (−1.0) × 0.5 + 0.787 × 1.0
m ≈ 1.787
f_c = 500 Hz × 2^{1.787} ≈ 1726 Hz
where
m_d: the total modulation for destination d, in that destination's own unit (octaves for cutoff)
m: that total for the cutoff destination in this example
Σ: sigma, "sum of": add up over every route i aimed at destination d
v_i: the current value of route i's source (env 0.5, LFO −1.0, velocity 100/127 ≈ 0.787)
k_i: route i's amount, here in octaves
f_c: the resulting cutoff before clamping, in hertz (Hz)
Hz: hertz
≈: approximately equal to
In words: multiply each source by its amount, add everything aimed at the same destination, then convert once.
```

The clamp keeps the filter within its safe range whatever combination of sources occurs, which matters because a matrix makes combinations you didn't plan for easy. (On a real filter, clamp to the range that design supports, often somewhat below Nyquist.)

Design points:

- Keep amounts **signed**, so any route can invert.
- Decide which sources are **per voice** (envelopes, velocity, key tracking) and which are **global** (a shared LFO, the mod wheel).
- Matrices cost CPU per route per update; on small hardware, keep the route list short and fixed-size.

## Control rate versus audio rate

Not every signal needs updating 48,000 times a second. Many synths compute modulation at a **control rate**, once per block, and only the audio path per sample.

```formula
f_ctl = f_s / B = 48000 Hz / 32 = 1500 Hz
T_B = B / f_s = 32 / 48000 Hz ≈ 0.67 ms
U = T × f_ctl = 0.001 s × 1500 Hz = 1.5
where
f_ctl: the control rate, in hertz (Hz): updates per second
f_s: the sample rate, 48,000 Hz
B: the block size, 32 samples
T_B: how long one block lasts, in milliseconds (ms)
U: how many control updates happen during an event of length T
T: the event's duration, here a 1 ms attack, 0.001 s
s: seconds
ms: milliseconds
Hz: hertz, per second
≈: approximately equal to
In words: one update per block gives 1,500 updates a second, so a 5 Hz LFO gets 300 per cycle but a 1 ms attack only 1.5.
```

At 48 kHz with 32-sample blocks the control rate is 1.5 kHz, and each block lasts 0.67 ms. That's plenty for a 5 Hz LFO (300 updates per cycle). It's not enough for:

- **Fast envelopes:** a 1 ms attack would be about 1.5 control steps, a staircase you'll hear as a click or buzz.
- **Fast or stepped modulation of gain and cutoff:** the block-rate staircase is the zipper noise from the envelopes lesson.
- **Audio-rate modulation:** modulating pitch at audio frequencies is FM (lesson 1), and it creates sidebands either side of the carrier (below). It must run per sample.

```formula
f_sb = f_car ± k × f_mod
where
f_sb: the frequency of one sideband, in hertz (Hz)
f_car: the carrier frequency (the oscillator being modulated), in Hz
f_mod: the modulator frequency, in Hz
k: a whole number 1, 2, 3...; each value gives one pair of sidebands
±: plus or minus: one sideband above the carrier and one below
Hz: hertz
In words: sidebands sit either side of the carrier, spaced at multiples of the modulator frequency.
```

A 5 Hz LFO puts its sidebands only 5 Hz apart, too close to hear as separate tones, so you hear a wobble (vibrato). A 220 Hz modulator on a 440 Hz carrier puts them at 220, 660, 880 Hz and so on: new tones, which a block-rate staircase cannot produce correctly.

Common compromise: compute modulation sources at control rate, then **linearly interpolate** the result across the block (or feed it into per-sample smoothers), and run anything fast or audible (amp envelope, audio-rate FM) per sample.

> [!note] Exponential versus linear FM
> Applying an oscillator to pitch *in octaves* (exponential FM, as you would for vibrato) is not symmetric in hertz. In a quick numpy check, a 5 Hz LFO at ±1 octave on 440 Hz gave an average frequency of 494.5 Hz, roughly 2 semitones sharp. At vibrato depths (±1 semitone) the average was 440.4 Hz, a negligible shift. For deep audio-rate FM, synths use **linear** FM (or phase modulation), which can keep the mean instantaneous frequency at the carrier (for zero-mean linear modulation). Perceived pitch and tuner readings depend on the resulting spectrum and analysis method; they are not guaranteed by that arithmetic mean.

The ±1-octave check computed this instantaneous frequency:

```formula
f(t) = f_0 × 2^{D × sin(2π × r × t)}
f(t) = 440 Hz × 2^{sin(2π × 5 × t)}
where
f(t): the instantaneous frequency at time t, in hertz (Hz)
f_0: the unmodulated frequency, 440 Hz
D: the depth in octaves: 1 for ±1 octave, 1/12 for ±1 semitone
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
r: the LFO rate, 5 Hz
t: time, in seconds
Hz: hertz
In words: the frequency swings between 220 Hz (half) and 880 Hz (double); the upper half-swing adds 440 Hz but the lower one removes only 220 Hz, so the average sits above 440 Hz, at about 494.5 Hz.
```

## Putting it together

A complete basic voice now looks like this, with the per-sample and control-rate parts marked:

```diagram
per block (control rate):
  LFO, mod wheel, matrix sums
     |  interpolate / smooth
     v
per sample (audio rate):
  osc(pitch) -> filter(cutoff, res)
     -> amp(amp env * velocity)
```

That's a playable monophonic subtractive synth. The roadmap's suggested exercise for this lesson is to apply an LFO to amplitude or pitch, then explain what you hear in terms of rate, depth and units.

## Key takeaways

- LFOs are slow phase-accumulator oscillators; bipolar for "around" a value, unipolar for "one way".
- Modulate pitch in semitones or cents and cutoff in octaves, then convert with `2 ** x`; a fixed depth in hertz instead gives different musical intervals at different base pitches and is appropriate for linear FM.
- Velocity, key tracking, mod wheel and envelopes are the main expressive sources; a matrix sums signed amounts per destination, then clamps.
- Control-rate modulation (once per block) is fine for slow LFOs but not for fast envelopes or audio-rate FM; interpolate or run those per sample.
- Deep exponential FM shifts mean instantaneous frequency; linear FM and PM give different spectra and are common choices for audio-rate modulation.

## Further reading

- [Low-frequency oscillation — Wikipedia](https://en.wikipedia.org/wiki/Low-frequency_oscillation)
- [Vibrato — Wikipedia](https://en.wikipedia.org/wiki/Vibrato)
- [Tremolo — Wikipedia](https://en.wikipedia.org/wiki/Tremolo)
- [Cent (music) — Wikipedia](https://en.wikipedia.org/wiki/Cent_(music))
- [MIDI 1.0 core specifications — MIDI Association](https://midi.org/midi-1-0-core-specifications)
- [Frequency modulation synthesis — Wikipedia](https://en.wikipedia.org/wiki/Frequency_modulation_synthesis)
- [Synthesizer — Wikipedia](https://en.wikipedia.org/wiki/Synthesizer)
