---
id: emb-control-to-audio-spsc-ring
sourceLesson: emb-control-to-audio
title: "A bounded SPSC event queue"
level: advanced
minutes: 4
summary: "Exactly one producer writes the publication index and one consumer writes the release index."
---

## Pattern 2: single-producer/single-consumer ring buffer

For **events** (note on, note off, a preset load), every message matters. Dropping or overwriting one causes stuck notes. Use a **queue**. On real-time systems the standard choice is a **lock-free single-producer/single-consumer (SPSC) ring buffer**:

- A fixed array, allocated at start-up.
- `head`: the next slot to write. **Only the producer writes it.**
- `tail`: the next slot to read. **Only the consumer writes it.**
- Because each index has exactly one writer, no lock is needed: just atomic loads and stores with the right ordering.

> [!analogy] Real-world analogy: Numbered pigeonholes between two clerks
> A post clerk puts letters into a row of numbered pigeonholes and moves a "next to fill" marker. A second clerk collects them in order and moves a "next to collect" marker. When every hole is full, the post clerk keeps the letter back rather than stuffing a hole twice.
>
> **How it maps:** The pigeonholes are the fixed array, the two markers are `head` and `tail`, and each marker has only one clerk allowed to move it. The full rule is the refused push.
>
> **Where it stops:** The clerks see each other's actions in order. A processor or compiler may make a marker update visible before the letter itself, so the release/acquire ordering is essential, not optional.

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

The mathematical model uses increasing counters and reduces them modulo capacity for array slots. Real fixed-width unsigned counters wrap: use the same unsigned width for subtraction, use a power-of-two capacity below the counter modulus, and prevent producers from advancing past capacity. The unsigned difference between the producer and consumer counters is the number of waiting items. An empty queue has no waiting items; a full queue has as many as its capacity. Array positions wrap around while FIFO order follows the counters, so a low array index need not hold the oldest item.

With a power-of-two capacity and unsigned integers, `h - t` stays correct even after the counters wrap around, and `h mod CAP` can be computed cheaply as `h & (CAP - 1)`, as the Python below does.

A single-threaded Python simulation of the index logic (it cannot show the concurrency, only the arithmetic):

```python
CAP = 4                 # power of two
# For power-of-two capacity only.
MASK = CAP - 1
buf = [None] * CAP
head = 0   # written only by producer
tail = 0   # written only by consumer

# Arithmetic model: no concurrent Python
# here.
def push(item):
    global head
    if head - tail == CAP:
        # Full: refuse without overwriting.
        return False
    # Slot writes precede publication.
    buf[head & MASK] = item
    head += 1               # publish
    return True

def pop():
    global tail
    if tail == head:
        return None         # empty
    # Consume the item before releasing
    # space.
    item = buf[tail & MASK]
    tail += 1               # release slot
    return item

# The fifth and sixth pushes must be
# refused.
for n in range(6):
    print("push", n, push(n))
print("pop", pop(), pop())
print("push 6", push(6), "push 7", push(7))
print("drain", [pop() for _ in range(5)])
```

```output
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

## Key takeaways
- Exactly one producer writes the publication index and one consumer writes the release index.
- Queue arithmetic, memory ordering, capacity and overflow recovery are separate responsibilities.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [Atomics ordering — C++ working draft](https://eel.is/c++draft/atomics.order)
