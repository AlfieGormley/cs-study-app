---
id: midi-fundamentals-encode-decode-trace
title: Build and decode complete messages
level: basic
minutes: 5
sourceLesson: midi-fundamentals
summary: Trace status, channel, key and velocity separately, and check MIDI and audio paths independently.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Building and reading messages

Here is the byte-level construction in Python. Your firmware will do the same with integers and bit operations.

```python
def note_on(channel, note, velocity):
    # Inputs are prevalidated MIDI values.
    # Convert displayed channel to
    # wire form.
    status = 0x90 | (channel - 1)
    return bytes([status, note, velocity])

def note_off(channel, note, velocity=64):
    # Use the explicit Note Off status.
    status = 0x80 | (channel - 1)
    return bytes([status, note, velocity])

# Output is hexadecimal bytes in wire order.
print(note_on(1, 60, 100).hex(" "))
print(note_on(10, 36, 127).hex(" "))
print(note_off(16, 69).hex(" "))
```

```output
90 3c 64
99 24 7f
8f 45 40
```

Read the first line: `0x90` is Note On, channel nibble 0 (channel 1); `0x3C` is 60, middle C; `0x64` is velocity 100.

Decoding goes the other way. Shift the status byte right by four bits to get the message type, and mask off its top nibble to get the wire channel:

```formula
M = S >> 4
ch = (S & 0x0F) + 1
M = 0x93 >> 4 = 0x9
ch = (0x93 & 0x0F) + 1 = 3 + 1 = 4
where
M: the message type, the status byte's top nibble, in hexadecimal: 8 = Note Off, 9 = Note On, B = Control Change
S: the received status byte, here 0x93
ch: the channel as people number it, 1 to 16
>>: bitwise right shift, moving every bit down by the given number of places and discarding the bits that fall off; shifting by 4 keeps just the top nibble
&: bitwise AND, which keeps only the bits that are set in both values; AND with 0x0F (binary 0000 1111) keeps just the low nibble
0x: prefix meaning hexadecimal (base 16)
In words: the top four bits say what kind of message it is, and the bottom four bits plus one say which channel.
```

Then fold velocity-0 note ons into note offs at the earliest point, so the rest of the synth only ever sees one kind of "off":

```python
# Fragment assumes one valid note message.
def describe(msg):
    status, note, vel = msg
    kind = status >> 4      # top nibble
    ch = (status & 0x0F) + 1
    # Both legal endings become one action.
    is_off = kind == 0x8 or (
        kind == 0x9 and vel == 0)
    if is_off:
        return f"ch{ch} off {note}"
    if kind == 0x9:
        return f"ch{ch} on {note} vel {vel}"
    return "other"

print(describe(bytes([0x93, 0x40, 0x50])))
print(describe(bytes([0x93, 0x40, 0x00])))
print(describe(bytes([0x83, 0x40, 0x40])))
```

```output
ch4 on 64 vel 80
ch4 off 64
ch4 off 64
```

## A worked example

A sequencer plays a two-note phrase on channel 3: key 64 (E above middle C) at velocity 90, released, then key 67 (G) at velocity 110, released. On the wire, using explicit note offs with the recommended release velocity of 64:

```
92 40 5A   note on  ch3 key 64 vel 90
82 40 40   note off ch3 key 64
92 43 6E   note on  ch3 key 67 vel 110
82 43 40   note off ch3 key 67
```

Twelve bytes, about 3.84 ms of wire time in total. The receiver needs to know only the channel it is listening on to decide whether to act on them.

## Pitfalls to design out early

- **Ignoring velocity-0 note on.** Stuck notes. Normalise it in the parser.
- **Channel off-by-one.** Your synth "doesn't respond" because it listens on 0x01 while the Digitakt sends on 0x00.
- **Assuming 8-bit values.** Data bytes never exceed 127. A value of 128 or more is a status byte; MIDI real-time statuses can interleave without replacing the current message.
- **Treating MIDI as sound.** If you hear nothing, check the audio path separately from the MIDI path. A MIDI monitor on the computer can prove the MIDI half works.
- **Unmatched note offs.** The specification requires a transmitter to send a note off for every note on. Your receiver still has to cope with missing ones; the later stuck-note unit covers recovery.

## Key takeaways
- Trace status, channel, key and velocity separately, and check MIDI and audio paths independently.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
