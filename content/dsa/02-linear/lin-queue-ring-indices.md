---
id: lin-queue-ring-indices
title: Ring-buffer indices and constant pointer work
level: advanced
minutes: 3
sourceLesson: lin-queues
summary: Wrap the next write slot round after the physical array end.
---

FIFO removal should advance a front position rather than shift all waiting elements. A fixed ring keeps a positive capacity and a live count. The example assumes single-threaded access; adding concurrent producers or consumers needs a separate synchronisation protocol.

## Circular buffers

A **circular buffer** (ring buffer) is a fixed array whose end wraps round to its start. Track the index of the front (`head`) and the number of items (`count`). When the buffer is not full, the next free slot at the back is `count` places after `head`, wrapping round to slot 0 when it runs off the end:

```formula reference
back = (head + count) mod capacity
where
back: the slot index where the next enqueued item is written
head: the slot index of the item at the front (the next to be dequeued)
count: how many items are in the buffer now
capacity: the number of slots in the array
mod: modulo: the remainder after dividing; 6 mod 4 = 2. It makes indices wrap round, so they always stay between 0 and capacity − 1. Python writes it %
In words: start at the front, step forward one slot per stored item, and wrap round to the start of the array when you pass the end.
```

With capacity 4, the front item in slot 2 and one item stored, the next item goes in slot 3; the one after that wraps round to slot 0, back at the start of the array. In Python this is `(head + count) % capacity`.

> [!analogy] Real-world analogy: Hours on a clock face
> On a 12-hour clock, five hours after 10 o'clock is 3 o'clock, not 15 o'clock: the count wraps round past 12 and starts again.
>
> **How it maps:** The clock positions are the buffer's slots, the current hour is `head`, and counting forward `count` hours finds the back. Wrapping past 12 is the wrap-round step (`% capacity` in Python) that keeps every index inside the array.
>
> **Where it stops:** A clock has no notion of empty or full slots, and its numbers run 1 to 12, whereas array slots are numbered from 0 up to one less than the capacity. The buffer must also refuse a write when every slot is in use, which the next unit covers.

Dequeuing just advances `head`. Nothing shifts.

```
capacity 4. enqueue A B C,
dequeue twice, enqueue D E F:

slot:   0   1   2   3
       [E | F | C | D]
                ^ head = 2
dequeue order: C, D, E, F
```

```python
class RingQueue:
    def __init__(self, cap):
        valid = isinstance(cap, int)
        if not valid or cap < 1:
            raise ValueError("cap >= 1")
        self.buf = [None] * cap
        self.cap = cap
        self.head = 0
        self.count = 0

    def enqueue(self, x):
        if self.count == self.cap:
            raise OverflowError("full")
        n = self.head + self.count
        # Wrap the next write slot at
        # capacity.
        i = n % self.cap
        # Write into the free logical back
        # slot.
        self.buf[i] = x
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            raise IndexError("empty")
        h = self.head
        x = self.buf[h]
        self.buf[h] = None   # drop the ref
        # Advance the front without
        # shifting.
        self.head = (h + 1) % self.cap
        self.count -= 1
        return x
```

## Key takeaways
- Wrap the next write slot round after the physical array end.
- Clear a dequeued slot so its old object need not stay alive.

## Further reading
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
