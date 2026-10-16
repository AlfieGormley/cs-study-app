---
id: syn-modulation-matrix
title: Envelope amounts and a modulation matrix
level: intermediate
minutes: 5
summary: Envelope amounts and a modulation matrix.
sourceLesson: syn-modulation
---

## Envelope, velocity and other sources

The most important modulation in a subtractive synth is the **filter envelope**: a second ADSR, scaled by an *amount*, added to the cutoff. Short attack and decay with low sustain give the classic pluck or "squelch". Like pitch, cutoff should be modulated in **octaves**:

```formula
o = e A_oct
f_c = f_base 2^{o}
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

- **Velocity:** an encoded note-attack performance value, often related to how fast a key was pressed; its exact physical mapping depends on the controller. In MIDI 1.0 it's a 7-bit value (1–127 for a sounding note; a note-on with velocity 0 means note-off). Mapping velocity to both level and cutoff makes harder notes louder *and* brighter, like acoustic instruments.
- **Key tracking:** the note number itself, so the filter opens for higher notes and timbre stays consistent across the keyboard.
- **Mod wheel** (MIDI CC 1), **aftertouch** and **pitch bend:** performance controls often mapped to vibrato depth or cutoff. In conventional MIDI 1.0, pitch bend and CC 1 are per channel; polyphonic key pressure can address a note, while channel pressure applies to the channel. Using separate channels changes how “global” controls should be assigned.
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

# Each destination has its own musical unit.
for s, d, amt in routes:
    mod[d] += src[s] * amt

base_cut, note_hz = 500.0, 440.0

# Convert the full-precision octave sum
# once.
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

Here the envelope adds 1.5 octaves, the LFO subtracts 0.5 and velocity 100 adds about 0.787. The full-precision sum is used in the exponent: a displayed rounded octave sum should not be substituted as though it were exact. The result is approximately 1,726 Hz. As a formula:

```formula
m_d = Σ v_i k_i
m = (0.5 × 3) + (−1 × 0.5) + (100 / 127)
m ≈ 1.787
f_c = 500 Hz × 2^{m} ≈ 1726 Hz
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

## Key takeaways

- Scale sources in each destination’s own units and add contributions before conversion.
- Distinguish per-voice from channel-wide or global sources.
- Keep route counts bounded and clamp to the actual filter range.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [MIDI message summary — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI control changes — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
