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

Scale the envelope by the requested octave amount. A full envelope with a three-octave amount opens the filter by three doublings; a half-height envelope contributes half that musical interval. Other routes add their own signed octave contributions.

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

Here the envelope adds 1.5 octaves, the LFO subtracts 0.5 and velocity 100 adds about 0.787. The full-precision sum is used in the exponent: a displayed rounded octave sum should not be substituted as though it were exact. The result is approximately 1,726 Hz. The useful reading of that result is:

The envelope opens the filter, the negative LFO contribution partly closes it, and the positive velocity contribution opens it further. Sum those octave contributions first, then perform one frequency conversion and apply the supported-range clamp.

For the modest values shown, the clamp bounds the result between its illustrative endpoints. Arbitrarily large finite octave sums can overflow during exponentiation before that clamp runs; validate inputs and bound the octave sum before conversion in production code. A matrix makes combinations you did not plan for easy. (On a real filter, clamp to the range that design supports, often somewhat below Nyquist.)

Design points:

- Keep amounts **signed**, so any route can invert.
- Decide which sources are **per voice** (envelopes, velocity, key tracking) and which are **global** (a shared LFO, the mod wheel).
- Matrices cost CPU per route per update; on small hardware, keep the route list short and fixed-size.

> [!analogy] Real-world analogy: Several adjustments on one thermostat
> Several controls can ask for warmer or cooler settings, but their adjustments must share one unit before they can be combined.
>
> **How it maps:** Each route has a signed amount. Contributions to one destination use the same units, are added, and then converted and limited.
>
> **Where it stops:** A modulation matrix is not necessarily a feedback controller; its sources can change much faster than room temperature.

## Key takeaways

- Scale sources in each destination’s own units and add contributions before conversion.
- Distinguish per-voice from channel-wide or global sources.
- Keep route counts bounded and clamp to the actual filter range.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [MIDI message summary — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI control changes — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
