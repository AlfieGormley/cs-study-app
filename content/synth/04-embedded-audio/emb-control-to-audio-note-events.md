---
id: emb-control-to-audio-note-events
sourceLesson: emb-control-to-audio
title: "Preserve note transitions as events"
level: advanced
minutes: 2
summary: "Polled state can lose intermediate transitions; events preserve their order within capacity."
---

## Pattern 3: event queues for notes

Represent notes as **events**, not as polled state. If the callback samples "is key 60 down?" once per block, a note-on followed by a note-off within the same block vanishes. A queue preserves transitions in order provided it does not overflow; overflow needs the recovery policy above.

```
message: { type, note, velocity }

callback(in, out, n):
  for _ in range(MAX_EVENTS_PER_BLOCK):
    m = midi_q.pop()
    if m == EMPTY: break
    if m.type == NOTE_ON:  voices.start(m)
    if m.type == NOTE_OFF: voices.release(m)
  render n samples
```

Keep parsing (turning raw MIDI bytes into messages) in the UART interrupt or the main loop, and keep the callback's job to applying messages. Pick one place to push from: if both the UART interrupt and the main loop push into the same queue, it is no longer an SPSC arrangement and the lock-free design above is unsafe. The diy-synth roadmap's MIDI exercise asks for exactly this separation, with diagnostic logging outside the callback. To log what arrived, push a copy to a second queue that the main loop prints.

The same pattern runs the other way: the callback pushes meter levels or a "clipped" flag to a queue or atomic that the main loop displays.

## Key takeaways
- Polled state can lose intermediate transitions; events preserve their order within capacity.
- Bound the events processed per block and keep a single producer per SPSC queue.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
