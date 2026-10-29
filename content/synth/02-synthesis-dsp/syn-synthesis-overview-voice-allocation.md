---
id: syn-synthesis-overview-voice-allocation
title: Polyphony, shared filters and voice stealing
level: basic
minutes: 4
summary: Polyphony, shared filters and voice stealing.
sourceLesson: syn-synthesis-overview
---

## Monophonic and polyphonic

A **monophonic** synth has one voice: it plays one note at a time. A **polyphonic** synth has several voices and can play chords. *Paraphonic* designs share some sound-shaping stages across several pitches, commonly a filter and its envelope. Amplifier and triggering arrangements vary by instrument.

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
        # Timestamp note starts, not audio
        # time.
        self.t += 1
        ids = range(len(self.note))
        free = [v for v in ids
                if self.note[v] is None]
        if free:
            v = free[0]
        else:            # steal oldest
            v = min(ids, key=lambda i:
                    self.start[i])
        # Reassign state in the fixed pool.
        self.note[v] = n
        self.start[v] = self.t
        return v

    def note_off(self, n):
        for v, x in enumerate(self.note):
            if x == n:
                # Sketch: no release-tail
                # tracking.
                self.note[v] = None

p = PolyAlloc(2)
print([p.note_on(n) for n in (60, 64, 67)])
# [0, 1, 0]: 67 steals voice 0 from 60
```

This sketch marks a voice free as soon as its key is released, so a voice still sounding its release tail can be reused abruptly. Real voice allocators track the envelope state, prefer voices that have finished, and fade a stolen voice out over a few milliseconds to avoid a click (covered in the neighbouring synthesis units).

The following is an **offline policy sketch**, not callback-ready allocation code. Its note arrays are a fixed voice pool, but the temporary list and Python runtime are unsuitable for a hard real-time callback. Note-off handling here frees a voice immediately rather than waiting for its envelope; repeated same-pitch/channel note matching is deliberately simplified. A production allocator must define that policy and track completion of release tails.

## Cost and choice

For the illustrated design with one oscillator, one filter and two envelopes per voice, 8 independent voices require 8 oscillator states, 8 filter states and 16 envelopes. Shared LFOs and output effects need not multiply with the voice count. On a microcontroller, measure the busiest supported combinations on the target board, including shared effects and control handling. Leave processing headroom for variation; a desktop experiment or average voice cost does not guarantee callback deadlines. A mono synth is the smallest complete instrument, and a well-structured monophonic voice becomes one voice of a poly synth later.

> [!analogy] Real-world analogy: A room with a fixed number of chairs
> When every chair is occupied, seating someone new means asking someone else to leave.
>
> **How it maps:** The chairs are the voice pool. An idle voice is an empty chair; stealing chooses an occupied voice to reassign.
>
> **Where it stops:** A released note may still have an audible tail, and fading that tail is an audio transition problem, not just a seating policy.

## Key takeaways

- A fixed voice pool prefers idle voices before stealing.
- Shared filtering shapes all notes together; independent voices permit separate articulation.
- Budget per-voice work plus shared processing, and fade audible stolen voices.

## Further reading

- [Matriarch manual — Moog](https://cdn.inmusicbrands.com/Moog/Matriarch/Matriarch_Manual_012023.pdf)
- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
