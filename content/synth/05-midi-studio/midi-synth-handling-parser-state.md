---
id: midi-synth-handling-parser-state
title: Trace a MIDI parser state machine
level: intermediate
minutes: 4
sourceLesson: midi-synth-handling
summary: Test single-data-byte messages, interrupted messages, SysEx termination and orphan data on the computer.
---

## Parsing: a small state machine

The parser must cope with everything the specification allows:

- channel messages with one or two data bytes;
- **running status** (data bytes with no new status byte);
- **MIDI real-time messages** (single bytes `F8`–`FF`) arriving anywhere, even mid-message;
- SysEx of any length without accumulating its payload;
- garbage: data bytes before any status, undefined status bytes, a device plugged in mid-stream.

The state is small: the running status byte, the data bytes collected so far, and whether we are inside a SysEx.

```python
# Data lengths for supported System Common.
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
        # SysEx content is
        # deliberately discarded.
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
        # Collect only the
        # required data bytes.
        self.data.append(b)
        need = data_len(self.rs)
        if len(self.data) < need:
            return []
        # Emit only once the
        # message is complete.
        msg = (self.rs, *self.data)
        self.data = []
        if self.rs >= 0xF0:
            self.rs = None  # sys common
        return [msg]

# Print complete messages, not raw byte
# arrival.
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

```output
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

This mirrors the receiver rules in the specification's appendix: store the status on channel messages, clear it on System Exclusive and System Common, leave it alone for MIDI real-time messages, and ignore data bytes when there is no status. Undefined System Common bytes (`F4`, `F5`) clear it too, and undefined MIDI real-time bytes (`F9`, `FD`) are simply ignored.

This teaching parser discards SysEx payload rather than implementing patch dumps. Its `rs` field temporarily holds the current System Common status until that message completes; only channel statuses persist across completed messages. Input to `feed` is one actual UART byte, an integer from zero to 255.

The parser emits raw tuples. A separate dispatcher must handle System Reset by resetting synth and parser state to the chosen documented power-up state. Other recognised real-time events do not disturb an unfinished message. The normalisation step turns channel tuples into events your synth understands, and this is where `9n kk 00` becomes a note off and messages for other channels are dropped.

> [!tip] Test the parser on your computer first
> Feed it recorded streams, hand-written edge cases and random bytes. Random input must never crash it or emit a message with a data value above 127. Bugs found here cost seconds; the same bugs found on hardware cost an evening.

## Key takeaways
- Test single-data-byte messages, interrupted messages, SysEx termination and orphan data on the computer.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
