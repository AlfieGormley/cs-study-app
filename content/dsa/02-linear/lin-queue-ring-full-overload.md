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

Use nonnegative logical counters for this model; fixed-width machine counters need an explicit wraparound and overflow protocol. Option 3 with a **power-of-two** capacity lets you replace `% cap` with a cheap **bit mask** `& (cap - 1)`:

```formula reference
i mod cap = band(i, cap − 1)
where
i: an ever-increasing head or tail counter
cap: the buffer capacity, which must be a power of two (2, 4, 8, 16, ...)
mod: modulo: the remainder after dividing by cap
band: the bitwise AND function: compares two numbers bit by bit, keeping a 1 only where both have a 1. Written & in C, Java and Python
In words: when the capacity is a power of two, the remainder after dividing by it is just the counter's lowest bits, which a single cheap bitwise AND instruction extracts. With any other capacity the shortcut gives wrong slots.
```

For example, with eight slots, counter 13 (binary 1101) masked with 7 (binary 0111) keeps 0101, slot 5, the same as the remainder of 13 divided by 8. The Linux kernel's `kfifo` relies on this, which is why it rounds sizes to powers of two.

### Growing and bounding

A ring buffer can grow like a dynamic array: allocate double the space and copy the items across in queue order, "unwrapping" them. Java ArrayDeque also grows a circular array, but OpenJDK 21 roughly doubles small buffers and grows larger ones by about 50%, with additional adjustments for required capacity.

Often you don't want it to grow. A bounded queue configured to block or reject producers provides **backpressure**: when consumers fall behind, producers block or are refused, instead of memory growing until the process dies. Audio drivers, network card receive rings and high-throughput designs like the LMAX Disruptor all use fixed-size rings.

> [!analogy] Real-world analogy: A restaurant with a small waiting area
> A busy restaurant has a few chairs by the door. When the chairs are full, the host asks new arrivals to wait outside or come back later instead of packing the lobby until nobody can move.
>
> **How it maps:** The chairs are the bounded buffer, the kitchen is the consumer, and arriving diners are producers. Turning people away or making them wait outside is backpressure: blocking or rejecting `put` once the queue is full.
>
> **Where it stops:** A full waiting area does not make the kitchen cook faster; only more cooks, simpler dishes or fewer diners change throughput. Diners may also give up and leave, whereas a blocked producer thread simply waits unless it was given a timeout.

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
