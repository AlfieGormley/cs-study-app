---
id: lin-queue-ring-full-overload
title: Full ring buffers and bounded overload
level: advanced
minutes: 4
sourceLesson: lin-queues
summary: A count, reserved slot or monotonic counters distinguishes full from empty.
---

The preceding unit implemented a ring with a count. Alternative representations must still distinguish its full and empty states. This unit connects capacity policy to overload: accepting work faster than it can be completed builds a backlog regardless of how cheap an enqueue is.

### Full or empty?

If you store `head` and `tail` indices instead of a count, `head == tail` is ambiguous: it is true both when the buffer is empty and when it is full. The usual fixes:

1. Keep a **count** (as above).
2. **Waste one slot**: declare the buffer full when `(tail + 1) % cap == head`, so a full buffer holds one fewer item than the physical slot count and `head == tail` can only mean empty.
3. Use ever-increasing head and tail counters and compare `tail - head` with the capacity, taking indices `% cap` only when touching the array.

Use nonnegative logical counters for this model; fixed-width machine counters need an explicit wraparound and overflow protocol. Option 3 with a **power-of-two** capacity lets you replace `% cap` with a cheap **bit mask** `& (cap - 1)`. When the capacity is a power of two, the remainder is just the lowest bits of the counter, and a bitwise AND keeps exactly those bits:

```formula
i mod cap = band(i, cap − 1)
13 mod 8 = band(13, 7) = 5
where
i: an ever-increasing head or tail counter
cap: the buffer capacity, which must be a power of two (2, 4, 8, 16, ...)
mod: modulo: the remainder after dividing by cap
band: the bitwise AND function: compares two numbers bit by bit, keeping a 1 only where both have a 1. Written & in C, Java and Python
In words: for a power-of-two capacity, the remainder after dividing by the capacity is just the counter's lowest bits, which one cheap AND instruction extracts.
```

Worked through in binary: 13 is 1101 and 7 is 0111, so the AND keeps 0101, which is 5, the same as 13 mod 8. With a capacity that isn't a power of two, such as 6, the trick fails: 13 mod 6 = 1 but the bitwise result from 13 and 5 is 5. The Linux kernel's `kfifo` works this way.

### Growing and bounding

A ring buffer can grow like a dynamic array: allocate double the space and copy the items across in queue order, "unwrapping" them. Java ArrayDeque also grows a circular array, but OpenJDK 21 roughly doubles small buffers and grows larger ones by about 50%, with additional adjustments for required capacity.

Often you don't want it to grow. A bounded queue configured to block or reject producers provides **backpressure**: when consumers fall behind, producers block or are refused, instead of memory growing until the process dies. Audio drivers, network card receive rings and high-throughput designs like the LMAX Disruptor all use fixed-size rings.

### Arrival rate versus service rate

With five thousand arrivals and one thousand completions per second, an unbounded queue accumulates four thousand extra items every second. After ten minutes it holds about 2.4 million items if the rates stay constant and it started empty. A new item behind that backlog waits about forty minutes at the same consumer rate.

Blocking or rejecting producers at a finite capacity prevents unlimited queue storage, but it does not make consumers faster. Improving throughput requires more service capacity, batching, or reducing accepted work. Storing backlog on disk changes the storage limit and durability policy rather than the basic rate imbalance.

## Key takeaways
- A count, reserved slot or monotonic counters distinguishes full from empty.
- A bound exposes overload but does not increase consumer throughput.

## Further reading
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [ArrayDeque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html)
- [Linux — circular-buffer conventions](https://docs.kernel.org/core-api/circular-buffers.html)
