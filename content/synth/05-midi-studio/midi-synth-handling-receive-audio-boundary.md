---
id: midi-synth-handling-receive-audio-boundary
title: Separate receiving from audio work
level: intermediate
minutes: 2
sourceLesson: midi-synth-handling
summary: Receive into bounded storage, count overflow, and keep parsing, waiting and logging outside the audio deadline.
---

The preceding MIDI units established the message formats. The implementation units cover what firmware has to do with them: turn a stream of bytes into events, decide which note a monophonic synth should play, make sure notes always stop, and turn controller values into smooth parameter changes.

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

- **Receiving** happens in an interrupt (or via DMA). It should only push each byte into a fixed-size ring buffer. At 31,250 baud successive bytes can complete every 320 µs at the nominal bit rate.
- **Parsing and note logic** run outside the audio callback, in the main loop or a control task, draining the buffer.
- **The audio callback** consumes a bounded number of queued note events in order, applies them to its voice state, and smooths latest-value control parameters. It must never wait on MIDI, allocate memory, or print logs.

How data crosses from the control code to the audio callback (atomics, a lock-free queue, or double buffering) depends on your platform, and is covered with embedded programming. The rule for now: the audio callback must never block.

```text
on_uart_byte(b):            # interrupt
    if not fifo.push(b):
        overflow_count += 1  # never block

control_loop():
    while fifo.pop(b):
        for event in parser.feed(b):
            handle(event)
```

This is architectural pseudocode, not executable Python: buffer, parser and event interfaces must be supplied by the platform. An interrupt may receive batches through a hardware FIFO or DMA rather than one callback per byte.

Count overflows rather than ignoring them. A lost note-off byte is a future stuck note, and the counter tells you it happened.

## Key takeaways
- Receive into bounded storage, count overflow, and keep parsing, waiting and logging outside the audio deadline.

## Further reading
- [Bounded audio-callback work — PortAudio](https://portaudio.com/docs/v19-doxydocs/writing_a_callback.html)
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
