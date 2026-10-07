---
id: midi-synth-handling
title: Handling MIDI inside a synth
level: intermediate
minutes: 16
summary: Parsing a MIDI byte stream robustly with a state machine, note priority for a monophonic synth, preventing stuck notes, and mapping CC values to synth parameters without zipper noise.
---

The last two lessons covered what MIDI messages look like. This one covers what your firmware has to do with them: turn a stream of bytes into events, decide which note a monophonic synth should play, make sure notes always stop, and turn controller values into smooth parameter changes.

The code here is Python, so you can run and test the logic on your computer first. On the synth, the same logic runs in firmware. Where timing and threads matter, the lesson uses short language-neutral pseudocode.

## Where MIDI handling runs

A typical embedded synth has three activities:

```diagram
UART RX interrupt  ->  byte FIFO
                          |
main loop / control task: parse,
  note priority, CC mapping
                          |
           event queue + parameters
                          |
audio callback: oscillators,
  envelopes, smoothing
```

- **Receiving** happens in an interrupt (or via DMA). It should only push each byte into a fixed-size ring buffer. At 31,250 baud a new byte arrives at most every 320 µs.
- **Parsing and note logic** run outside the audio callback, in the main loop or a control task, draining the buffer.
- **The audio callback** consumes a bounded number of queued note events in order, applies them to its voice state, and smooths latest-value control parameters. It must never wait on MIDI, allocate memory, or print logs.

How data crosses from the control code to the audio callback (atomics, a lock-free queue, or double buffering) depends on your platform, and is covered with embedded programming. The rule for now: the audio callback must never block.

```
on_uart_byte(b):            # interrupt
    if not fifo.push(b):
        overflow_count += 1  # never block

control_loop():
    while fifo.pop(b):
        for event in parser.feed(b):
            handle(event)
```

Count overflows rather than ignoring them. A lost note-off byte is a future stuck note, and the counter tells you it happened.

## Parsing: a small state machine

The parser must cope with everything the specification allows:

- channel messages with one or two data bytes;
- **running status** (data bytes with no new status byte);
- **real-time bytes** (`F8`–`FF`) arriving anywhere, even mid-message;
- SysEx of any length;
- garbage: data bytes before any status, undefined status bytes, a device plugged in mid-stream.

The state is small: the running status byte, the data bytes collected so far, and whether we are inside a SysEx.

```python
SYS_LEN = {0xF1: 1, 0xF2: 2, 0xF3: 1}

def data_len(status):
    hi = status & 0xF0
    if hi in (0xC0, 0xD0):
        return 1
    if hi < 0xF0:
        return 2
    return SYS_LEN.get(status, 0)

class Parser:
    def __init__(self):
        self.rs = None      # running status
        self.data = []
        self.sysex = False

    def feed(self, b):
        # 1. real-time: act, keep state
        if b in (0xF9, 0xFD):
            return []  # undefined real-time
        if b >= 0xF8:
            return [(b,)]
        # 2. any other status byte
        if b & 0x80:
            self.data = []
            self.sysex = (b == 0xF0)
            if b < 0xF0:       # channel msg
                self.rs = b
            elif b in SYS_LEN:  # sys common
                self.rs = b
            else:               # F0 F4-F7
                self.rs = None
                if b == 0xF6:   # tune req
                    return [(b,)]
            return []
        # 3. data byte
        if self.sysex or self.rs is None:
            return []           # ignore
        self.data.append(b)
        need = data_len(self.rs)
        if len(self.data) < need:
            return []
        msg = (self.rs, *self.data)
        self.data = []
        if self.rs >= 0xF0:
            self.rs = None  # sys common
        return [msg]

def show(stream):
    p = Parser()
    for b in stream:
        for m in p.feed(b):
            print(" ".join(
                f"{x:02X}" for x in m))

show([0x90, 0x3C, 0x64,  # note on
      0x40, 0x64,        # running st.
      0x3C, 0xF8, 0x00,  # clock inside
      0xF2, 0x00, 0x00,  # song pos
      0x3C, 0x00])       # orphan data
```

```
90 3C 64
90 40 64
F8
90 3C 00
F2 00 00
```

Trace the interesting parts:

1. `40 64` has no status byte; running status reuses `90`, giving a second Note On.
2. `F8` arrives between `3C` and `00`. It is emitted immediately and the half-built Note On survives, so `90 3C 00` still completes (a note off, since velocity is 0).
3. `F2 00 00` is a System Common message (Song Position). System Common **clears** running status, so the final `3C 00` has no status to attach to and is ignored.

This mirrors the receiver rules in the specification's appendix: store the status on channel messages, clear it on System Exclusive and System Common, leave it alone on real-time, and ignore data bytes when there is no status. Undefined System Common bytes (`F4`, `F5`) clear it too, and undefined real-time bytes (`F9`, `FD`) are simply ignored.

The parser emits raw tuples. A second step normalises them into events your synth understands, and this is where `9n kk 00` becomes a note off and messages for other channels are dropped.

> [!tip] Test the parser on your computer first
> Feed it recorded streams, hand-written edge cases and random bytes. Random input must never crash it or emit a message with a data value above 127. Bugs found here cost seconds; the same bugs found on hardware cost an evening.

## Note priority for a monophonic synth

A mono synth has one voice, but a player (or the Digitakt's chord feature) can hold several keys. The **note priority** rule decides which held key sounds:

- **Last note:** the most recently pressed key wins. Releasing it falls back to the previous one still held. It feels the most natural when playing from a sequencer or keyboard, and is a sensible default.
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
        if n in self.held:
            self.held.remove(n)
        self.held.append(n)
        return self.target()

    def note_off(self, n):
        if n in self.held:
            self.held.remove(n)
        return self.target()

events = [("on", 60), ("on", 64),
          ("on", 55), ("off", 55),
          ("off", 64), ("off", 60)]
for mode in ("last", "low", "high"):
    v = MonoVoice(mode)
    out = []
    for kind, n in events:
        f = v.note_on if kind == "on" \
            else v.note_off
        out.append(f(n))
    print(mode, out)
```

```
last [60, 64, 55, 64, 60, None]
low [60, 60, 55, 60, 60, None]
high [60, 64, 64, 64, 60, None]
```

`None` means no keys are held, so the gate closes and the envelope enters release. Two further design choices:

- **Retrigger or legato.** When the target changes while keys are still held, do you restart the envelope (retrigger) or just glide or jump the pitch (legato)? Many mono synths offer both.
- **Bounded memory.** In firmware the stack is a fixed array (say 16 entries, with oldest-dropping on overflow), never a growing list. Removing a key that isn't in the stack must be harmless.

## Stuck notes and how to prevent them

A stuck note is a voice that never receives the note off that should end it. The project brief asks for "no unintended stuck notes", so design against each cause.

| Cause | Defence |
|---|---|
| `9n kk 00` not treated as off | Normalise in the parser |
| Note off on another channel | Track notes per channel |
| Channel changed while held | Release all on change |
| Bytes lost (overflow, unplug) | Count overflows; panic |
| Two note ons, one note off | Note stack dedupes keys |
| Sustain pedal held | Defer offs until pedal up |

**Track held notes, not just "the current note".** If the synth remembers only the sounding note, a note off for an earlier key can be misapplied, or missed entirely. The note stack above gives correct behaviour for free.

**Implement the mode messages that silence notes.** All Notes Off (CC 123) and the mode changes 124–127 should release every note received via MIDI on that channel. The specification says All Notes Off should send voices into their **release** stage rather than cutting them abruptly. All Sound Off (CC 120) is the hard version: silence as soon as possible. A spec detail worth copying: while the sustain pedal (CC 64) is on, note offs **and** All Notes Off are remembered but not acted on until the pedal is released.

**Don't rely on All Notes Off alone.** The specification says receivers aren't required to recognise it, and transmitters should send individual note offs first. Treat it as a safety net.

**Give yourself a panic action.** A button (or a CC) that empties the note stack, closes the gate and resets pitch bend to centre is invaluable during development.

**Consider Active Sensing.** If your source sends `FE`, a receiver that stops hearing anything for about 300 ms should assume the cable came out and turn its voices off. If the source never sends `FE`, behave normally.

## Mapping CC values to parameters

A CC gives you 0–127. Your synth parameter has a real range and a natural scale. Mapping has three parts.

### 1. Choose the curve

For **frequencies and times**, use an exponential curve, so that equal knob movements give equal musical intervals:

```python
def cc_to_cutoff(v, lo=20.0, hi=20000.0):
    # exponential: equal steps = equal
    # musical intervals
    return lo * (hi / lo) ** (v / 127)

for v in (0, 32, 64, 96, 127):
    print(v, round(cc_to_cutoff(v), 1))
```

```
0 20.0
32 114.0
64 649.9
96 3704.6
127 20000.0
```

With a linear map over the same range, the step from 0 to 1 jumps from 20 Hz to about 177 Hz (more than three octaves), and half the knob covers 10–20 kHz where little changes audibly. Exponential spreads the ~10 octaves evenly, at about 0.94 semitones per step.

For **mix levels** use a decibel-style curve, and for **switches** use the spec convention (≤63 off, ≥64 on).

### 2. Use more resolution where it matters

At 128 steps, a slow filter sweep can produce audible stepping. Options: accept 14-bit pairs (CC n with CC n+32) where your controller sends them, and in every case **smooth** the value in the audio callback.

### 3. Smooth in the audio domain

The control code only sets a *target*. The audio callback moves the real parameter towards it a little each sample (a one-pole smoother is the usual tool, covered with synthesis DSP). That removes zipper noise and makes timing jitter in MIDI arrival less audible.

```
control code, on CC 74 value v:
    cutoff_target = cc_to_cutoff(v)
    publish(cutoff_target)   # atomic store

audio callback, per sample:
    cutoff += k * (cutoff_target - cutoff)
    filter.set_cutoff(cutoff)
```

Keep a single **CC map** table in one place: CC number, parameter, curve and range. Print it into your project docs. You will need it when you set up the Digitakt's MIDI track CC slots in lesson 6.

## Key takeaways
- Receive bytes in an interrupt into a fixed ring buffer, parse outside the audio callback, and count overflows instead of blocking.
- A parser needs only running status, a data-byte count and a SysEx flag. Real-time bytes are handled immediately without disturbing state; SysEx and System Common clear running status; orphan data bytes are ignored.
- A mono synth keeps a stack of held notes and applies last-, low- or high-note priority after every change; an empty stack closes the gate.
- Stuck notes come from missed or misread note offs. Normalise velocity-0 note ons, track notes per channel, honour All Notes Off with sustain-pedal deferral, and keep a panic action.
- Map CCs with curves that suit the parameter (exponential for frequency), and smooth the target in the audio callback to avoid zipper noise.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
