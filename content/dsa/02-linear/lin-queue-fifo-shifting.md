---
id: lin-queue-fifo-shifting
title: FIFO queues and the cost of front shifting
level: advanced
minutes: 3
sourceLesson: lin-queues
summary: A queue serves arrivals in their original order.
---

A **queue** is a line at a shop: people join at the back and are served from the front. The first one in is the first one out: **FIFO**. Where a stack serves the most recent arrival, a queue serves the one that has waited longest.

Queues are everywhere in real systems. Print jobs, network packets in a router, tasks waiting for a thread pool, messages in broker partitions or queue services, keystrokes waiting for your program to read them: all queues. Inside algorithms, the queue is what makes **breadth-first search** explore nearest-first.

## The operations

| Operation | What it does | Target cost |
|---|---|---|
| `enqueue(x)` | Add x at the back | O(1) |
| `dequeue()` | Remove from the front | O(1) |
| `peek()` | Look at the front | O(1) |
| `is_empty()` | Anything waiting? | O(1) |

```
dequeue <- [ A | B | C | D ] <- enqueue
          front           back
```

## The wrong way: a plain list

The obvious Python queue is a list with `append` and `pop(0)`:

```python
q = []
q.append("A")   # enqueue, O(1)
q.pop(0)        # dequeue, O(n)!
```

`pop(0)` shifts every remaining element one slot left. Draining a queue of n items this way moves n − 1 elements on the first dequeue, n − 2 on the next, and so on down to 0:

```formula
moves = (n − 1) + (n − 2) + ... + 1 + 0
moves = n(n − 1) / 2
moves ≈ n^2 / 2
where
moves: the total number of element moves to empty the queue
n: the number of items in the queue at the start
≈: approximately equal to; for large n, n − 1 is about n
In words: each dequeue shifts everything still waiting, so the total grows with the square of the queue length.
```

For 100,000 items that is about 100,000² / 2 = 5 billion moves; a proper queue would do 100,000 cheap operations. That is O(n²) for the whole drain, or O(n) per dequeue. The bug is invisible in tests with 10 items and catastrophic in production with a million.

Two structures fix it: a linked list with head and tail pointers (dequeue at the head, enqueue at the tail, both O(1)), or, usually better, a **circular buffer**.

## Key takeaways
- A queue serves arrivals in their original order.
- Repeated list-front removal shifts a quadratic total of elements.

## Further reading
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
- [ArrayDeque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html)
