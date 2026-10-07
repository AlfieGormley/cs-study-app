---
id: emb-control-to-audio
title: Getting control data to the audio code
level: advanced
minutes: 16
summary: How knob values and MIDI events cross safely from the foreground to the audio callback - why volatile is not synchronisation, atomic single values, single-producer/single-consumer ring buffers, event queues for notes, and smoothing parameters on the receiving side.
---

Lesson 6 split the firmware into two worlds: the **audio callback**, which runs from an interrupt once per block and must never wait, and the **foreground** (main loop and lower-priority work), which reads knobs, parses MIDI and drives the display. Every useful synth needs data to cross between them. A knob moves in the foreground; the filter that reacts lives in the callback.

Getting this wrong produces the worst kind of bug: rare, timing-dependent and hard to reproduce. A stuck note once an hour. A click when two parameters change together. This lesson gives you a small set of safe patterns, described in language-neutral terms so they apply whatever language and platform you end up using.

## The foreground/background split

Draw the data paths explicitly. For a simple synth:

```diagram
 knobs --> [main loop: scan, smooth, map]
                 |
                 | params (atomic)
                 v
 MIDI --> [UART ISR] --> [parse] --> [queue]
                                       |
                                       v
                          [audio callback]
                                       |
                 meters, clip flag <---+
```

For each arrow, ask: who writes, who reads, and can the reader interrupt the writer (or run on another core) halfway through? On a single-core MCU, the callback can interrupt the main loop at *any* instruction. On a multi-core computer such as a Raspberry Pi, both sides may genuinely run at the same time.

## What can go wrong

**Torn reads.** The main loop is writing a value that takes more than one memory operation (a 64-bit number on a 32-bit core, or a group of related fields). The callback interrupts between the two halves and reads half old, half new.

**Stale values.** The compiler sees that a loop never changes a variable and keeps it in a register, so the loop never sees the other side's update.

**Reordering.** The writer does "write data, then set ready flag". The compiler, and on some processors the hardware, may make the flag visible before the data. The reader sees "ready" and reads garbage.

**Lost updates.** Both sides do read-modify-write on the same variable (`count = count + 1`). One side's update overwrites the other's.

## Why `volatile` is not synchronisation

C and C++ (and some other languages) have a `volatile` keyword. It tells the compiler that every access to that variable must really happen, in program order *relative to other volatile accesses*, because something outside the program (a hardware register, an interrupt) may change it. That fixes *stale values* for that one variable.

It does **not**:

- make a read-modify-write such as `x = x + 1` indivisible;
- prevent a multi-word value from tearing;
- order ordinary (non-volatile) memory accesses around it, so "write data, then set volatile flag" can still be reordered as far as the data is concerned;
- provide the memory barriers that multi-core processors need.

The diy-synth roadmap states it directly: "`volatile` alone is not thread synchronisation". The Linux kernel documentation has a whole page explaining why kernel code should not use `volatile` for this, and the C++ reference says the same for threads: use atomics. `volatile` remains correct for its real purpose, memory-mapped hardware registers.

## Pattern 1: atomic single values

For one independent parameter (cutoff, gain, a mode number), use your language's **atomic** type. An atomic guarantees:

- the value is read and written in one indivisible step (no tearing);
- a store becomes visible to loads on the other side, so a loop polling it will see the update (the compiler cannot hoist the load out of the loop the way it can for a plain variable);
- with the right **memory ordering**, writes before it are visible to a reader who sees it.

One caveat for interrupts: the atomic must be **lock-free**. If the hardware cannot do the operation natively, the library may fall back to an internal lock, and an interrupt that hits while the foreground holds that lock will deadlock. On 32-bit Cortex-M parts, 8-, 16- and 32-bit atomics (including `float`) are normally lock-free, but 64-bit ones (`double`, `int64_t`) usually are not, because Armv7-M has no 64-bit exclusive load/store. In C++, check `is_always_lock_free`.

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

### Several parameters that must change together

If a preset change sets ten parameters, atomics individually can let the callback see five new and five old. Options:

- **Send the change as one message** through a queue (pattern 2). The callback applies all ten at a block boundary.
- **Double buffer with acknowledgement:** allow only one unacknowledged publication. Fill the inactive set, then release-store its index and generation together. The callback acquire-loads that publication, finishes all reads of the old set, and release-stores the adopted generation as its acknowledgement. Only after an acquire-load sees that exact acknowledgement may the producer reuse the old set. A counter increment at block start alone is insufficient: it can advance before the callback loads the new publication. The callback never waits.
- On Teensy, PJRC's audio library offers `AudioNoInterrupts()` and `AudioInterrupts()` around a group of settings so they "all take effect at the same time". That briefly holds off the audio update from the foreground; keep the section short.

## Pattern 2: single-producer/single-consumer ring buffer

For **events** (note on, note off, a preset load), every message matters. Dropping or overwriting one causes stuck notes. Use a **queue**. On real-time systems the standard choice is a **lock-free single-producer/single-consumer (SPSC) ring buffer**:

- A fixed array, allocated at start-up.
- `head`: the next slot to write. **Only the producer writes it.**
- `tail`: the next slot to read. **Only the consumer writes it.**
- Because each index has exactly one writer, no lock is needed: just atomic loads and stores with the right ordering.

```
push(item):            # producer only
  h = head.load_relaxed()
  t = tail.load_acquire()
  if h - t == CAP: return FULL
  buf[h mod CAP] = item
  head.store_release(h + 1)

pop():                 # consumer only
  t = tail.load_relaxed()
  h = head.load_acquire()
  if t == h: return EMPTY
  item = buf[t mod CAP]
  tail.store_release(t + 1)
  return item
```

Why the orderings: the producer must write the item *before* publishing the new `head` (release); the consumer must see that `head` *before* reading the item (acquire). The same pairing protects the slot being freed in the other direction.

The indices count up forever and are reduced modulo the capacity. With a power-of-two capacity and unsigned integers, `h - t` stays correct even after the counters wrap around.

A single-threaded Python simulation of the index logic (it cannot show the concurrency, only the arithmetic):

```python
CAP = 4                 # power of two
MASK = CAP - 1
buf = [None] * CAP
head = 0   # written only by producer
tail = 0   # written only by consumer

def push(item):
    global head
    if head - tail == CAP:
        return False        # full: drop
    buf[head & MASK] = item
    head += 1               # publish
    return True

def pop():
    global tail
    if tail == head:
        return None         # empty
    item = buf[tail & MASK]
    tail += 1               # release slot
    return item

for n in range(6):
    print("push", n, push(n))
print("pop", pop(), pop())
print("push 6", push(6), "push 7", push(7))
print("drain", [pop() for _ in range(5)])
```

```
push 0 True
push 1 True
push 2 True
push 3 True
push 4 False
push 5 False
pop 0 1
push 6 True push 7 True
drain [2, 3, 6, 7, None]
```

When full, the producer **refuses** rather than waiting. Count overflow and use an explicit recovery policy: for note-event loss, set a separate lock-free panic/reset flag so the callback can release held voices and discard invalid pending state. Silently dropping note offs is not safe. The callback never waits; an empty queue means no events are available.

### Sizing the queue

DIN MIDI delivers at most 3,125 bytes a second. Complete three-byte messages take 0.96 ms, but running-status note messages need only two bytes (0.64 ms) and real-time events one byte (0.32 ms). Size the queue for the actual event mix, maximum interval between drains and bursts; USB can deliver much larger bursts. A 64-event queue is an example, not a guaranteed bound.

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

Keep parsing (turning raw MIDI bytes into messages) in the UART interrupt or the main loop, and keep the callback's job to applying messages. Pick one place to push from: if both the UART interrupt and the main loop push into the same queue, it is no longer single-producer and the lock-free design above is unsafe. The diy-synth roadmap's MIDI exercise asks for exactly this separation, with diagnostic logging outside the callback. To log what arrived, push a copy to a second queue that the main loop prints.

The same pattern runs the other way: the callback pushes meter levels or a "clipped" flag to a queue or atomic that the main loop displays.

## Pattern 4: smooth on the receiving side

The callback now receives correct values, but they arrive in steps: knob scans at around 1 kHz, MIDI CCs in 128 coarse steps. Jumping a gain or cutoff by a step at a block boundary makes **zipper noise**. Smooth again, at audio rate, inside the callback:

**Per-sample one-pole** towards the latest target:

```
a = 1 - exp(-1 / (tau * fs))   # at init
per sample:
  cur = cur + a * (target - cur)
```

For τ = 5 ms at 48 kHz, a ≈ 0.004158; for 20 ms, a ≈ 0.001041. Compute `a` once at start-up, not per sample.

**Linear ramp per block:** step from the old value to the new across the block, adding (new − old) / N each sample: with N = 48, one forty-eighth of the change per sample. Simple, and it guarantees arrival by the block's end.

Why smooth here and not only in the foreground? The foreground can only deliver values as often as it runs. The receiving side knows the sample rate, so it is the only place that can make the change continuous. The foreground smoothing from lesson 3 is about rejecting knob noise; this smoothing is about removing steps.

## Choosing a pattern

| Data | Pattern |
|---|---|
| Single knob value | Atomic, smooth in callback |
| Grouped parameter change | One message or double buffer |
| Note on/off, program change | SPSC event queue |
| Meters, clip flag (back) | Atomic or SPSC queue |
| Debug logging | Queue to main loop |

## Key takeaways
- Map every data path: who writes, who reads, and whether one can interrupt (or run alongside) the other.
- `volatile` stops the compiler caching one variable; it does not prevent tearing, lost updates or reordering. Use atomics.
- Latest-value data (knobs) suits atomics; every-message data (notes) needs a queue.
- An SPSC ring buffer has one writer per index, so it needs no lock; it refuses when full instead of waiting.
- Smooth parameters at audio rate on the receiving side to remove zipper noise.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
