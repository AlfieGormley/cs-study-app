---
id: emb-control-to-audio-preset-ownership
sourceLesson: emb-control-to-audio
title: "Publish a complete parameter set"
level: advanced
minutes: 2
summary: "Updating parameters individually does not publish a whole parameter set together."
---

A preset changes several related parameter values. The foreground produces a complete set and the callback adopts it at a block boundary. Each publication and acknowledgement must use an atomic operation that is suitable for the actual platform. A **preset generation** is a version number for one complete parameter publication; carry it with the buffer index in a target-supported atomic representation.

## Several parameters that must change together

If a preset change sets ten parameters, atomics individually can let the callback see five new and five old. Options:

- **Send the change as one message** through a queue (pattern 2). The callback applies all ten at a block boundary.
- **Double buffer with acknowledgement:** allow only one unacknowledged publication. Fill the inactive set, then release-store its index and preset generation together. The callback acquire-loads that publication, finishes all reads of the old set, and release-stores the adopted preset generation as its acknowledgement. Only after an acquire-load sees that exact acknowledgement may the producer reuse the old set. A counter increment at block start alone is insufficient: it can advance before the callback loads the new publication. The callback never waits.
- On Teensy, PJRC's audio library offers `AudioNoInterrupts()` and `AudioInterrupts()` around a group of settings so they "all take effect at the same time". That briefly holds off the audio update from the foreground; keep the section short.

> [!analogy] Real-world analogy: Swapping a printed menu
> A restaurant changes its menu by handing diners a complete new card, not by crossing out dishes one at a time while people read. The old cards are reprinted only after they have been collected.
>
> **How it maps:** The complete parameter set is the menu card. Publishing one finished set stops the callback seeing half old and half new values. Waiting for the old card to come back is the acknowledgement before the producer reuses that buffer.
>
> **Where it stops:** The callback never waits for the producer. The publication and acknowledgement must use target-supported atomic operations with the correct ordering, which a handed-over card does not need.

## Key takeaways
- Updating parameters individually does not publish a whole parameter set together.
- An immutable queued message or acknowledged buffer ownership protects the full set.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [Atomics ordering — C++ working draft](https://eel.is/c++draft/atomics.order)
