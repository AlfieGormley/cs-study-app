---
id: midi-synth-handling-mono-priority
title: Track held notes and choose a target
level: intermediate
minutes: 3
sourceLesson: midi-synth-handling
summary: Track held keys separately from the sounding target, and make priority, retrigger and overflow policies explicit.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Note priority for a monophonic synth

A mono synth has one voice, but a player (or the Digitakt's chord feature) can hold several keys. The **note priority** rule decides which held key sounds:

- **Last note:** the most recently pressed key wins. Releasing it falls back to the previous one still held. It is one possible policy for a sequenced or keyboard-played monophonic voice.
- **Low note:** the lowest held key wins, whatever order the keys were pressed in.
- **High note:** the highest held key wins.

Which to offer is a design decision; some mono synths let the player choose it as a setting.

The key data structure is a **note stack**: the list of held keys in press order. The rule is applied to the stack after every change.

```python
class MonoVoice:
    def __init__(self, mode="last"):
        self.mode = mode
        self.held = []   # in press order

    def target(self):
        if not self.held:
            return None      # gate off
        if self.mode == "low":
            return min(self.held)
        if self.mode == "high":
            return max(self.held)
        return self.held[-1]  # last

    def note_on(self, n):
        # This policy coalesces
        # repeated keys.
        if n in self.held:
            self.held.remove(n)
        self.held.append(n)
        return self.target()

    # An unheld key is harmless to
    # this policy.
    def note_off(self, n):
        if n in self.held:
            self.held.remove(n)
        return self.target()

events = [("on", 60), ("on", 64),
          ("on", 55), ("off", 55),
          ("off", 64), ("off", 60)]
# Output lists the target after every event.
for mode in ("last", "low", "high"):
    v = MonoVoice(mode)
    out = []
    for kind, n in events:
        f = v.note_on if kind == "on" \
            else v.note_off
        out.append(f(n))
    print(mode, out)
```

```output
last [60, 64, 55, 64, 60, None]
low [60, 60, 55, 60, 60, None]
high [60, 64, 64, 64, 60, None]
```

`None` means no keys are held, so the gate closes and the envelope enters release. This example deliberately keeps one entry per key. Repeated Note Ons for the same channel and key are coalesced, so one Note Off removes that key; this is a simplified monophonic allocation policy, not a universal rule for stacked voices. Transmitters still owe a matching Note Off for every Note On.

Two further design choices:

- **Retrigger or legato.** When the target changes while keys are still held, do you restart the envelope (retrigger) or just glide or jump the pitch (legato)? Many mono synths offer both.
- **Bounded memory.** In firmware the stack is a fixed array (say 16 entries, with oldest-dropping on overflow), never a growing list. Removing a key that isn't in the stack must be harmless.

## Key takeaways
- Track held keys separately from the sounding target, and make priority, retrigger and overflow policies explicit.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
