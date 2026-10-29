---
id: midi-fundamentals-din-wire-time
title: Count DIN MIDI wire time
level: basic
minutes: 3
sourceLesson: midi-fundamentals
summary: Each DIN byte costs ten bit-times, so a three-byte message occupies the cable for just under a millisecond and chords arrive as a quick ripple.
---

## The serial link

Classic MIDI 1.0 runs over a 5-pin DIN cable as an asynchronous serial link: one wire pair, one bit at a time. The MIDI specifications fix the format:

- **31,250 bits per second** (±1%).
- Each byte is framed as **1 start bit, 8 data bits, 1 stop bit**, no parity (often written 8-N-1).
- Bytes are sent least significant bit first.

The framing is the part beginners forget. A byte holds 8 data bits, but it occupies **10 bit-times** on the wire, so one byte takes **320 µs** (millionths of a second). A complete three-byte message such as Note On therefore occupies the cable for about **0.96 ms**, just under a millisecond, provided the bytes are sent back to back. A slower or busier sender only makes it longer.

```formula reference
t_msg = (n N_bits) / R
where
t_msg: the time a complete message occupies the cable, in seconds (s)
n: the number of bytes in the message; 3 for a Note On (status byte plus two data bytes)
N_bits: the number of bits in one framed byte: 1 start + 8 data + 1 stop = 10
R: the bit rate (baud rate) of the link, in bits per second (bit/s); 31,250 bit/s for DIN MIDI
In words: count every framed bit, including start and stop bits, and divide by 31,250 bits per second; each DIN byte costs 320 µs, so three bytes take about 0.96 ms.
```

## Why it matters: chords become ripples

Because there is only one serial line, messages "at the same time" are really queued one after another. Ten three-byte Note On messages scheduled for one instant are 30 bytes, about 9.6 ms of wire time. The receiver cannot start the last note until its message has fully arrived, so the chord ripples over several milliseconds. Dense controller data sent alongside notes delays them further.

Two practical consequences follow:

- Saving bytes saves time. Running status (a later unit) drops repeated status bytes, which shortens a chord.
- The same budget limits throughput: DIN MIDI can carry only about a thousand three-byte messages per second.

Your microcontroller's UART (universal asynchronous receiver-transmitter) does the framing for you. You configure it for 31,250 baud, 8-N-1, and it hands you whole bytes.

## Key takeaways
- Each DIN MIDI byte occupies 10 bit-times (start, 8 data, stop), which is 320 µs at 31,250 bit/s.
- A back-to-back three-byte message takes just under 1 ms, so a ten-note chord is spread over several milliseconds.
- Fewer bytes (for example through running status) means less wire time and less delay for the notes queued behind them.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
