---
id: syn-synthesis-overview-note-priority
title: Held notes and monophonic priority
level: basic
minutes: 3
summary: Held notes and monophonic priority.
sourceLesson: syn-synthesis-overview
---

A monophonic synth plays one pitch at a time. This offline sketch assumes one channel and one held instance per note number. It deduplicates repeated note-ons; a receiver that permits stacked same-pitch events must define matching note-off semantics separately.

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
        # A repeat moves this pitch to
        # newest.
        if n in self.held:
            self.held.remove(n)
        self.held.append(n)
        return n            # note to play

    def note_off(self, n):
        if n in self.held:
            self.held.remove(n)
        # Fall back to the newest held
        # pitch.
        if self.held:
            return self.held[-1]
        return None         # start release

m = MonoVoice()
print(m.note_on(60), m.note_on(64),
      m.note_off(64), m.note_off(60))
# 60 64 60 None
```

When `note_off` returns a note, the voice glides or jumps back to it; `None` means start the release.

> [!warning] Stuck notes
> Every note-on must eventually be matched by a note-off for the same note, or a voice sounds forever. Handle the MIDI convention that a note-on with velocity 0 means note-off, and give yourself an "all notes off" escape. The project brief lists "no stuck notes" as a success criterion.

## Key takeaways

- A held-note stack allows last-note priority to return to an older held key.
- Treat MIDI note-on with velocity zero as a note-off.

## Further reading

- [Minimoog Model D user guide — Moog](https://cdn.inmusicbrands.com/Moog/Model%20D/Minimoog_Model_D_Manual.pdf)
- [MIDI message summary — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [Zero-velocity note-on discussion — MIDI Association](https://midi.org/community/midi-specifications/zero-velocity-note-on)
