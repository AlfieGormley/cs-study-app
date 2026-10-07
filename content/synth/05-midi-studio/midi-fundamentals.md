---
id: midi-fundamentals
title: MIDI fundamentals
level: basic
minutes: 12
summary: What MIDI actually carries (events, not audio), the MIDI 1.0 byte format, channels, note on/off, velocity and the note-on-with-velocity-0 rule, worked at the byte level.
---

MIDI (Musical Instrument Digital Interface) is the language your Digitakt will use to tell your synth what to play. It was published in 1983 and is still the standard way for instruments, sequencers and computers to talk to each other.

The most important idea in this lesson is also the simplest: **MIDI carries events, not sound.** A MIDI cable never carries a waveform. It carries short messages such as "key 60 went down on channel 1, quite hard" and "key 60 came back up". The receiving instrument decides what those events sound like.

## Events, not audio

Think of MIDI as a pianist's instructions written down at the moment they happen, not a recording of the piano.

| | MIDI | Audio |
|---|---|---|
| Carries | Events (note on, knob moved) | Sampled waveform |
| Size | 2–3 bytes per event | 48,000 samples/s per channel |
| Sound depends on | The receiver | Nothing; it is the sound |
| Cable | MIDI (DIN, TRS, USB) | Audio jack, USB audio |

This has practical consequences for your build:

- Your synth needs **two separate paths**: MIDI in (what to play) and audio out (the sound it makes). Connecting the Digitakt's MIDI OUT to your synth does nothing audible until your synth's audio output reaches a mixer or interface.
- A recorded MIDI part in Ableton is a list of events. Change the synth patch and the "recording" sounds different. A recorded audio part is fixed.
- MIDI is cheap. A note costs 3 bytes; the audio for that note might be hundreds of thousands of bytes.

## The serial link

Classic MIDI 1.0 runs over a 5-pin DIN cable as an asynchronous serial link. The MIDI electrical specification fixes the format:

- **31,250 bits per second** (±1%).
- Each byte is framed as **1 start bit, 8 data bits, 1 stop bit**, no parity (often written 8-N-1).
- So each byte costs 10 bit-times: 10 / 31,250 s = **320 µs**.
- Bytes are sent least significant bit first.

A three-byte message takes 3 × 320 µs = **0.96 ms**, roughly a millisecond. That figure matters later when we talk about chords and latency: ten notes "at once" are actually spread over about 10 ms.

Your microcontroller's UART (universal asynchronous receiver-transmitter) does this framing for you. You configure it for 31,250 baud, 8-N-1, and it hands you whole bytes.

## Status bytes and data bytes

Every MIDI 1.0 byte is one of two kinds, and you can tell which by looking at the top bit:

```
bit:   7 6 5 4 3 2 1 0
status 1 t t t c c c c   0x80-0xFF
data   0 v v v v v v v   0x00-0x7F
```

- A **status byte** has bit 7 set. It says what kind of message this is. For channel messages, the top four bits (`tttt` above, including the 1) are the message type and the bottom four (`cccc`) are the channel.
- A **data byte** has bit 7 clear, so it carries a value from **0 to 127** (7 bits).

This one-bit rule is what makes MIDI robust. If a receiver joins mid-stream or loses a byte, a non-real-time status byte supplies a new message boundary. Real-time bytes also have bit 7 set but may interrupt a message without resetting it. It is also why MIDI values run 0–127 rather than 0–255: the eighth bit is spent on telling status from data.

The specification says each status byte is followed by a fixed number of data bytes (one or two for channel messages), and a receiver must wait for all of them before acting. It also says receivers should ignore data bytes that are not preceded by a valid status byte, apart from one shortcut called running status, which the next lesson covers.

## Channels

MIDI 1.0 has **16 channels**. They let one cable address up to 16 independent instruments (or parts of a multitimbral instrument). Each receiver is set to listen on one channel (or all of them, "omni") and ignores channel messages for others.

The channel is in the low nibble of the status byte, numbered 0–15 on the wire. People and manuals number them 1–16. This off-by-one causes real bugs:

```
user channel  1  -> nibble 0x0
user channel 10  -> nibble 0x9
user channel 16  -> nibble 0xF
```

> [!warning] Channel 1 is 0 on the wire
> When the Digitakt's MIDI track is set to CHAN 1, your synth will see status bytes with channel nibble 0 (for example `0x90` for a note on), not nibble 1 (`0x91`). Store channels internally as 0–15 and add 1 only when displaying them.

## Note on and note off

The two messages your synth must handle first:

| Message | Status | Data 1 | Data 2 |
|---|---|---|---|
| Note Off | `0x8n` | key (0–127) | release velocity |
| Note On | `0x9n` | key (0–127) | velocity (0–127) |

`n` is the channel nibble. The key number identifies the note: the MIDI specification gives **middle C a value of 60**. Each step is a semitone, so 61 is C♯, 72 is the C an octave up.

Converting a key number to a frequency is a convention from the MIDI Tuning Standard and equal temperament: key 69 is A at 440 Hz, and each semitone multiplies frequency by 2^(1/12).

```python
def note_to_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)

for n in (60, 69, 36):
    print(n, round(note_to_hz(n), 2))
```

```
60 261.63
69 440.0
36 65.41
```

> [!note] Octave names differ, numbers don't
> Devices disagree about what to *call* note 60. Ableton Live's note ruler starts at C-2 (note 0), so Live calls middle C (60) **C3**. Elektron's Digitakt manuals number notes from C0 (note 0, range C0–G10); the original Digitakt manual states outright that MIDI note 60, middle C, is **C5**. Much other software calls it C4. The number 60 is what goes on the wire, so debug with numbers.

### Velocity

Velocity is how hard (strictly, how fast) the key was struck, 1–127. The specification leaves its interpretation to the receiver; it suggests that if velocity controls loudness, the mapping should preferably be exponential, and that devices without velocity sensing should send **64**.

### Note on with velocity 0 means note off

This rule trips up nearly every first MIDI implementation. The MIDI 1.0 specification gives two equivalent ways to end a note:

1. A Note Off message: `8n kk vv`.
2. A Note On message with velocity zero: `9n kk 00`.

It says a receiver **must be able to recognise either method, and should treat them identically**. Many transmitters prefer the second form because, combined with running status, a long run of notes can be sent without repeating the status byte.

If your synth treats `9n kk 00` as "start a note very quietly", notes will never end. That is a classic stuck-note bug.

## Building and reading messages

Here is the byte-level construction in Python. Your firmware will do the same with integers and bit operations.

```python
def note_on(channel, note, velocity):
    # channel is 1-16 as users see it
    status = 0x90 | (channel - 1)
    return bytes([status, note, velocity])

def note_off(channel, note, velocity=64):
    status = 0x80 | (channel - 1)
    return bytes([status, note, velocity])

print(note_on(1, 60, 100).hex(" "))
print(note_on(10, 36, 127).hex(" "))
print(note_off(16, 69).hex(" "))
```

```
90 3c 64
99 24 7f
8f 45 40
```

Read the first line: `0x90` is Note On, channel nibble 0 (channel 1); `0x3C` is 60, middle C; `0x64` is velocity 100.

Decoding goes the other way. Split the status byte into its nibbles, and fold velocity-0 note ons into note offs at the earliest point, so the rest of the synth only ever sees one kind of "off":

```python
def describe(msg):
    status, note, vel = msg
    kind = status >> 4      # top nibble
    ch = (status & 0x0F) + 1
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

```
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
- **Assuming 8-bit values.** Data bytes never exceed 127. A value of 128 or more is a status byte; real-time statuses can interleave without replacing the current message.
- **Treating MIDI as sound.** If you hear nothing, check the audio path separately from the MIDI path. A MIDI monitor on the computer can prove the MIDI half works.
- **Unmatched note offs.** The specification requires a transmitter to send a note off for every note on. Your receiver still has to cope with missing ones; lesson 3 covers how.

## Key takeaways
- MIDI carries short event messages, not audio. Your synth needs a MIDI input path and a separate audio output path.
- DIN MIDI runs at 31,250 bit/s with 10 bits per byte, so each byte takes 320 µs and a 3-byte message about 0.96 ms.
- Bit 7 distinguishes status bytes (0x80–0xFF) from data bytes (0x00–0x7F), so values are 0–127 and receivers can resynchronise.
- Channels are 1–16 to humans but 0–15 in the status byte's low nibble.
- Note On is `9n kk vv`, Note Off is `8n kk vv`, middle C is 60, and a Note On with velocity 0 must be treated exactly like a Note Off.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
