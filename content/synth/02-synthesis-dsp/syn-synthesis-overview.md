---
id: syn-synthesis-overview
title: Synthesis approaches and signal flow
level: basic
minutes: 11
summary: The main ways synths make sound (subtractive, additive, FM/PM, wavetable, sample-based, physical modelling), the classic subtractive voice, and how mono and poly synths allocate voices.
---

A synthesiser is a program (or circuit) that turns *control* information, such as "play note 60, fairly hard", into a stream of audio samples. Every design answers the same two questions:

- **Where does the raw sound come from?** A waveform, a recording, a mathematical model.
- **How is it shaped over time?** Filters, envelopes and modulation.

The different "kinds" of synthesis are mostly different answers to the first question. Before choosing one for your instrument, it helps to know what each costs and what it is good at.

## The main approaches

| Approach | Raw material | Shaped by |
|---|---|---|
| Subtractive | Bright waves (saw, square) | Filters remove harmonics |
| Additive | Many sine waves | Per-partial levels |
| FM / PM | Sines modulating sines | Modulation index |
| Wavetable | Stored single cycles | Scanning through tables |
| Sample-based | Recordings | Pitch shift, envelopes |
| Physical modelling | Model of a vibrating object | Model parameters |

### Subtractive

Start with a waveform rich in harmonics and **remove** what you don't want with a filter. A sawtooth through a low-pass filter whose cutoff falls over time gives the classic "pluck" or brass sound. This is the architecture of the Minimoog and most analogue synths, and it is the one you'll build first in this module because each block is simple and audible.

### Additive

Any periodic sound can be described as a sum of sine waves (the next-but-one lesson shows why). Additive synthesis builds the sound directly from those sines, each with its own frequency and level, often with its own envelope. It gives total control, but a low note can need hundreds of sines per voice, and controlling that many parameters musically is hard.

### FM and PM

In **frequency modulation** one oscillator (the *modulator*) varies the frequency of another (the *carrier*) at audio rate. This creates sidebands at the carrier frequency plus and minus multiples of the modulator frequency, so two sine oscillators can produce a complex spectrum. John Chowning developed it at Stanford from 1967 and Yamaha licensed it; the DX7 (1983) made it famous.

Yamaha's commercial "FM" (the DX7 included) is actually implemented as **phase modulation** (adding the modulator to the carrier's *phase* rather than its frequency). An industry-wide prevalence claim is omitted because no reliable survey of implementations was available for this review. The two are mathematically closely related: phase-modulating with a signal is the same as frequency-modulating with its derivative. A practical advantage of PM is that a modulator with a DC offset only shifts the carrier's phase, whereas in true FM it shifts the carrier's pitch. FM is cheap in CPU but notoriously hard to programme by ear.

### Wavetable

Store a set of single-cycle waveforms (a **wavetable**) and play one back with a phase accumulator, optionally sweeping or crossfading through the set to make the timbre evolve. Wolfgang Palm of PPG developed his multi-wavetable version in the late 1970s (Hal Chamberlin had described table-lookup wavetables in 1977, and Michael McNabb developed a similar idea independently); Waldorf instruments continue Palm's approach. Each table is cheap to play, but high notes alias unless you keep band-limited versions of each table (lesson 4).

### Sample-based

Play back recordings of real sounds, re-pitched by reading them faster or slower, then shape them with envelopes and filters. Realism is excellent; memory use is large, and expressive range is limited to what was recorded. Your Digitakt is a sample-based instrument.

### Physical modelling

Simulate the physics of a string, tube or membrane. The classic small example is **Karplus–Strong**: fill a short delay line with noise and feed it back through a gentle low-pass filter. The loop's length sets the pitch (roughly `fs / f0` samples) and the filter makes high harmonics die first, like a plucked string. Julius O. Smith's *Physical Audio Signal Processing* covers this family in depth.

> [!tip] A reasonable first instrument
> Subtractive is the usual first build because each block (oscillator, filter, amplifier, envelope, LFO) can be built and tested on its own. The project brief suggests a monophonic digital subtractive synth as an option; this module teaches every block it would need without committing you to it.

## The classic subtractive voice

A **voice** is everything needed to play one note. The textbook subtractive voice looks like this:

```diagram
 note pitch
     |
     v
 +-------+   +--------+   +-------+
 |  OSC  |-->| FILTER |-->|  AMP  |--> out
 +-------+   +--------+   +-------+
     ^            ^           ^
     |            |           |
    LFO      filter env    amp env
             (+ velocity)  (gate)
```

- **Oscillator (VCO/DCO):** generates a periodic waveform at the note's pitch.
- **Filter (VCF):** usually a resonant low-pass; its cutoff sets brightness.
- **Amplifier (VCA):** multiplies the signal by a gain, so the note can start and stop.
- **Envelopes:** time-varying control signals started by the key (the *gate*). One drives the amplifier, another typically sweeps the filter cutoff.
- **LFO:** a slow oscillator (below about 20 Hz) that wobbles pitch (vibrato), level (tremolo) or cutoff.

The "V" names come from analogue gear where each block was *voltage controlled*. In software the same structure holds: audio flows left to right, and control signals arrive from below.

Notice there are two kinds of signal. **Audio signals** run at the sample rate and you hear them. **Control signals** (envelopes, LFOs, knob positions, MIDI) change more slowly and steer the audio blocks. Keeping these separate is central to real-time design, as later lessons show.

## Monophonic and polyphonic

A **monophonic** synth has one voice: it plays one note at a time. A **polyphonic** synth has several voices and can play chords. *Paraphonic* designs sit between: several oscillators at different pitches share one filter and amplifier.

### Monophonic: note priority

When you hold two keys on a mono synth, which one sounds? That rule is **note priority**:

- **Last-note priority:** the most recently pressed key wins. Releasing it falls back to a key still held.
- **Low-note** or **high-note priority:** the lowest or highest held key wins.

Last-note priority needs a stack of held notes, otherwise releasing the newest note while an older one is held leaves silence or a stuck note:

```python
class MonoVoice:
    """Last-note priority, note stack."""
    def __init__(self):
        self.held = []

    def note_on(self, n):
        if n in self.held:
            self.held.remove(n)
        self.held.append(n)
        return n            # note to play

    def note_off(self, n):
        if n in self.held:
            self.held.remove(n)
        if self.held:
            return self.held[-1]
        return None         # start release

m = MonoVoice()
print(m.note_on(60), m.note_on(64),
      m.note_off(64), m.note_off(60))
# 60 64 60 None
```

When `note_off` returns a note, the voice glides or jumps back to it; `None` means start the release.

### Polyphonic: voice allocation

A poly synth has a fixed pool of voices (say 4 or 8). The **voice allocator** decides which voice plays each new note:

1. If a voice is free, use it.
2. If all are busy, **steal** one. Common choices: the oldest note, the quietest voice, or a voice already in its release phase.

```python
class PolyAlloc:
    """Free voice first, else oldest."""
    def __init__(self, voices):
        self.note = [None] * voices
        self.start = [0] * voices
        self.t = 0

    def note_on(self, n):
        self.t += 1
        ids = range(len(self.note))
        free = [v for v in ids
                if self.note[v] is None]
        if free:
            v = free[0]
        else:            # steal oldest
            v = min(ids, key=lambda i:
                    self.start[i])
        self.note[v] = n
        self.start[v] = self.t
        return v

    def note_off(self, n):
        for v, x in enumerate(self.note):
            if x == n:
                self.note[v] = None

p = PolyAlloc(2)
print([p.note_on(n) for n in (60, 64, 67)])
# [0, 1, 0]: 67 steals voice 0 from 60
```

This sketch marks a voice free as soon as its key is released, so a voice still sounding its release tail can be reused abruptly. Real allocators track the envelope state, prefer voices that have finished, and fade a stolen voice out over a few milliseconds to avoid a click (lesson 5).

> [!warning] Stuck notes
> Every note-on must eventually be matched by a note-off for the same note, or a voice sounds forever. Handle the MIDI convention that a note-on with velocity 0 means note-off, and give yourself an "all notes off" escape. The project brief lists "no stuck notes" as a success criterion.

## Cost and choice

Polyphony multiplies everything: 8 voices means 8 oscillators, 8 filters and 16 envelopes per sample. On a microcontroller this decides your CPU budget. A mono synth is the smallest complete instrument, and a well-structured mono voice becomes one voice of a poly synth later.

## Key takeaways

- Synthesis methods differ mainly in where the raw sound comes from: filtered rich waves, summed sines, modulated sines, stored cycles, recordings or physical models.
- The subtractive voice is oscillator → filter → amplifier, steered by envelopes and LFOs.
- Audio signals run at the sample rate; control signals steer them more slowly.
- Mono synths need a note-priority rule and a held-note stack; poly synths need a voice allocator and a stealing policy.
- Polyphony multiplies CPU cost per voice.

## Further reading

- [Subtractive synthesis — Wikipedia](https://en.wikipedia.org/wiki/Subtractive_synthesis)
- [Frequency modulation synthesis — Wikipedia](https://en.wikipedia.org/wiki/Frequency_modulation_synthesis)
- [Wavetable synthesis — Wikipedia](https://en.wikipedia.org/wiki/Wavetable_synthesis)
- [Karplus–Strong string synthesis — Wikipedia](https://en.wikipedia.org/wiki/Karplus%E2%80%93Strong_string_synthesis)
- [Physical Audio Signal Processing — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/pasp/)
- [Polyphony and monophony in instruments — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
