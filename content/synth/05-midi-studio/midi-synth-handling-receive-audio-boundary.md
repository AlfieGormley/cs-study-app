---
id: midi-synth-handling-receive-audio-boundary
title: Separate receiving from audio work
level: intermediate
minutes: 3
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

> [!analogy] Real-world analogy: a live radio studio
> A live radio presenter must keep talking on schedule. Letters arrive at the post room at any time; a producer opens them, sorts them and hands the presenter a short stack of prepared cards between links.
>
> **How it maps:** the post-room pigeonhole is the receive ring buffer, filled by the UART interrupt without waiting. The producer is the control loop that parses bytes into events and decides what they mean. The presenter is the audio callback: it reads only the cards already prepared, a bounded number at a time, and never stops broadcasting to wait for the post.
>
> **Where it stops:** a real pigeonhole can overflow and silently lose bytes, so firmware counts overflows. The hand-over between producer and presenter also needs a mechanism that is safe when both run at once (such as a lock-free queue), which a stack of paper cards does not illustrate.

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
- Split the work: the receive interrupt only stores bytes, the control loop parses them, and the audio callback consumes ready events.
- Receive into bounded storage and count overflows, because a lost note-off byte becomes a stuck note.
- Keep parsing, waiting, allocation and logging outside the audio callback's deadline.

## Further reading
- [Bounded audio-callback work — PortAudio](https://portaudio.com/docs/v19-doxydocs/writing_a_callback.html)
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
