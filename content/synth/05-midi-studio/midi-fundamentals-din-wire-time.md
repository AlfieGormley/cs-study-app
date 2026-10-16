---
id: midi-fundamentals-din-wire-time
title: Calculate DIN MIDI transmission time
level: basic
minutes: 3
sourceLesson: midi-fundamentals
summary: Count start and stop bits as well as data: a back-to-back three-byte DIN message takes 0.96 ms.
---

## The serial link

Classic MIDI 1.0 runs over a 5-pin DIN cable as an asynchronous serial link. The MIDI electrical specification fixes the format:

- **31,250 bits per second** (±1%).
- Each byte is framed as **1 start bit, 8 data bits, 1 stop bit**, no parity (often written 8-N-1).
- So each byte costs 10 bit-times, which works out at **320 µs** (calculated below).
- Bytes are sent least significant bit first.

How long does one byte take on the wire? Divide the number of bits in its frame by the number of bits the link sends each second. You use this whenever you need to know how quickly MIDI can deliver something.

```formula
t_byte = N_bits / R
t_byte = 10 bit / (31250 bit/s)
t_byte = 0.00032 s = 320 µs
where
t_byte: the time one framed byte occupies the cable, in seconds (s)
N_bits: the number of bits in one frame: 1 start bit + 8 data bits + 1 stop bit = 10 bits
R: the bit rate (baud rate) of the link, in bits per second (bit/s); 31,250 bit/s for DIN MIDI
bit: one binary digit, 0 or 1
s: seconds
µs: microseconds, millionths of a second (1 µs = 0.000001 s)
In words: one MIDI byte takes ten bit-times, and at 31,250 bits per second that is 320 millionths of a second.
```

A whole message is just its bytes sent one after another, so its time is the byte count times the DIN framed-byte duration:

```formula
t_msg = n t_byte
t_msg = 3 × 320 µs
t_msg = 960 µs ≈ 0.96 ms
where
t_msg: the time a complete message occupies the cable, in microseconds (µs) or milliseconds (ms)
n: the number of bytes in the message; 3 for a Note On (status byte plus two data bytes)
t_byte: the time per byte, 320 µs on DIN MIDI
µs: microseconds, millionths of a second
ms: milliseconds, thousandths of a second (1 ms = 1000 µs)
≈: approximately equal to
In words: a three-byte message takes just under one millisecond to send.
```

So a three-byte message takes about **0.96 ms**, roughly a millisecond. That figure matters later when we talk about chords and latency: ten three-byte notes "at once" are actually 30 bytes, about 9.6 ms of wire time, so they are spread over roughly 10 ms. This assumes the bytes are sent back to back with no gaps; a slower sender only makes it longer.

Your microcontroller's UART (universal asynchronous receiver-transmitter) does this framing for you. You configure it for 31,250 baud, 8-N-1, and it hands you whole bytes.

## Key takeaways
- Count start and stop bits as well as data: a back-to-back three-byte DIN message takes 0.96 ms.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
