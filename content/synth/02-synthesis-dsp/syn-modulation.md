---
id: syn-modulation
title: Modulation, LFOs and the modulation matrix
level: advanced
minutes: 15
summary: LFO rates, shapes and polarity; vibrato and tremolo with correct depth units; envelope and velocity modulation of the filter; a modulation matrix; and the trade-offs of control-rate versus audio-rate modulation.
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

Convert with `uni = (bi + 1) / 2`.

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

The LFO updates once per 32-sample block (1,500 times a second), so a 5 Hz cycle takes 300 updates. The tremolo gain swings between 0.5 and 1.0: depth 0.5 means "down to half volume", never above the original.

Two common LFO options:

- **Key sync / retrigger:** reset the LFO phase on each note so every note starts its wobble the same way. Free-running LFOs drift relative to the notes.
- **Tempo sync:** derive the rate from tempo. At 120 BPM a beat lasts 0.5 s, so one cycle per quarter note is 2 Hz.

## Vibrato and tremolo

**Vibrato** is periodic pitch variation; **tremolo** is periodic amplitude variation. (Some instruments and effects use the names loosely; synths use them precisely.)

**Pitch depth belongs in cents or semitones**, because pitch is heard logarithmically. Add the modulation in semitones, then convert:

```
f = f_note * 2 ** (semitones / 12)
```

| Vibrato depth | 440 Hz swings between |
|---|---|
| ±50 cents | 427.47 – 452.89 Hz |
| ±100 cents | 415.30 – 466.16 Hz |

A fixed depth in hertz would be wrong: ±10 Hz is a wide vibrato on a bass note and barely noticeable on a high one.

**Gain depth** is usually specified as a fraction of the level (or in dB). Applying `1 − depth · uni(lfo)` keeps the peak at the original level and avoids pushing the signal past full scale.

## Envelope, velocity and other sources

The most important modulation in a subtractive synth is the **filter envelope**: a second ADSR, scaled by an *amount*, added to the cutoff. Short attack and decay with low sustain give the classic pluck or "squelch". Like pitch, cutoff should be modulated in **octaves**:

```
oct = env * env_amount_octaves
cutoff = base * 2 ** oct
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

Here the envelope adds 1.5 octaves, the LFO subtracts 0.5 and velocity 100 adds 0.787, for a net +1.787 octaves: 500 Hz becomes 1,726 Hz. The clamp keeps the filter within its safe range whatever combination of sources occurs, which matters because a matrix makes combinations you didn't plan for easy. (On a real filter, clamp to the range that design supports, often somewhat below Nyquist.)

Design points:

- Keep amounts **signed**, so any route can invert.
- Decide which sources are **per voice** (envelopes, velocity, key tracking) and which are **global** (a shared LFO, the mod wheel).
- Matrices cost CPU per route per update; on small hardware, keep the route list short and fixed-size.

## Control rate versus audio rate

Not every signal needs updating 48,000 times a second. Many synths compute modulation at a **control rate**, once per block, and only the audio path per sample.

At 48 kHz with 32-sample blocks the control rate is 1.5 kHz, and each block lasts 0.67 ms. That's plenty for a 5 Hz LFO (300 updates per cycle). It's not enough for:

- **Fast envelopes:** a 1 ms attack would be about 1.5 control steps, a staircase you'll hear as a click or buzz.
- **Fast or stepped modulation of gain and cutoff:** the block-rate staircase is the zipper noise from the envelopes lesson.
- **Audio-rate modulation:** modulating pitch at audio frequencies is FM (lesson 1), and it creates sidebands at `fc ± k·fm`. It must run per sample.

Common compromise: compute modulation sources at control rate, then **linearly interpolate** the result across the block (or feed it into per-sample smoothers), and run anything fast or audible (amp envelope, audio-rate FM) per sample.

> [!note] Exponential versus linear FM
> Applying an oscillator to pitch *in octaves* (exponential FM, as you would for vibrato) is not symmetric in hertz. In a quick numpy check, a 5 Hz LFO at ±1 octave on 440 Hz gave an average frequency of 494.5 Hz, roughly 2 semitones sharp. At vibrato depths (±1 semitone) the average was 440.4 Hz, a negligible shift. For deep audio-rate FM, synths use **linear** FM (or phase modulation), which can keep the mean instantaneous frequency at the carrier (for zero-mean linear modulation). Perceived pitch and tuner readings depend on the resulting spectrum and analysis method; they are not guaranteed by that arithmetic mean.

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
