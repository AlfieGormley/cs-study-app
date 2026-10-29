---
id: emb-control-to-audio-atomic-latest
sourceLesson: emb-control-to-audio
title: "Publish a latest parameter value"
level: advanced
minutes: 2
summary: "Use an atomic type with target-verified lock-free operations."
---

## Pattern 1: atomic single values

For one independent parameter (cutoff, gain, a mode number), use your language's **atomic** type. A supported atomic operation guarantees:

- the value is read and written in one indivisible step (no tearing);
- loads and stores obey atomic coherence rules; a compiler cannot simply replace repeated atomic loads with one cached ordinary load. This is not a bounded-time freshness or scheduling guarantee;
- with the right **memory ordering**, writes before it are visible to a reader who sees it.

> [!analogy] Real-world analogy: A stadium scoreboard
> Spectators glance at a scoreboard whenever they like. If they miss a goal, the board still shows the current score, and the operator changes the whole number at once.
>
> **How it maps:** The atomic value is the scoreboard: the callback reads the latest value whenever it runs, and missing intermediate values does no harm. Changing the whole number at once corresponds to an indivisible store, so nobody reads half an update.
>
> **Where it stops:** A scoreboard announces nothing else. When a value also signals that other data is ready, it needs suitable memory ordering, and on interrupt-driven firmware the atomic must also be lock-free.

One caveat for interrupts: the atomic must be **lock-free**. If the hardware cannot do the operation natively, the library may fall back to an internal lock, and an interrupt that hits while the foreground holds that lock will deadlock. Armv7-M provides 8-, 16- and 32-bit exclusive access instructions, but no 64-bit exclusive pair. This does not by itself certify a language atomic implementation. Check the exact type, operation, compiler, ABI and alignment: in C++, inspect `is_always_lock_free`, target documentation and generated code. Even lock-free read-modify-write can retry; prefer documented bounded loads/stores for this pattern.

Pseudocode, where `store_release` and `load_acquire` stand for the language's atomic operations with release/acquire ordering:

```
shared cutoff: atomic float

main loop:
  c = map(smooth(read_knob(0)))
  cutoff.store_release(c)

callback:
  target = cutoff.load_acquire()
```

For a lone value that no other data depends on, the weakest ("relaxed") ordering is usually enough; release/acquire matters when the value *announces* other data. On a 32-bit MCU, an aligned 32-bit store is typically one instruction anyway, but write the atomic: it documents intent and stays correct if the code moves to a multi-core platform.

**Rule of thumb:** latest-value-wins data (a knob position) suits an atomic. If the callback misses an intermediate value, nothing is lost, because only the latest matters.

## Key takeaways
- Use an atomic type with target-verified lock-free operations.
- A lone latest value and a published payload need different ordering guarantees.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [Atomics ordering — C++ working draft](https://eel.is/c++draft/atomics.order)
