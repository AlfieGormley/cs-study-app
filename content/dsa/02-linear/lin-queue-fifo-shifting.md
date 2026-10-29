---
id: lin-queue-fifo-shifting
title: FIFO queues and the cost of front shifting
level: advanced
minutes: 3
sourceLesson: lin-queues
summary: A queue serves arrivals in their original order.
---

A **queue** adds items at the back and removes them from the front. The first one in is the first one out: **FIFO**. Where a stack serves the most recent arrival, a queue serves the one that has waited longest.

> [!analogy] Real-world analogy: A line at a shop counter
> People join the back of the line and the cashier serves whoever is at the front. In a narrow corridor, every time someone is served, everyone behind them shuffles one step forward.
>
> **How it maps:** Joining is `enqueue`, being served is `dequeue`, and the first to arrive is the first to leave. The shuffling corridor is a Python list used with `pop(0)`: every removal moves all the remaining items one slot. A better design keeps people still and moves a "now serving" marker instead, which is what a circular buffer does.
>
> **Where it stops:** Real people can give up and leave from the middle, or be let in early; a plain FIFO queue does not allow either. People shuffle forward all at once, so the line advances in one moment however long it is; a computer moves the items one after another, so `pop(0)` takes time proportional to the number still waiting.

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

```formula reference
moves = n(n − 1) / 2
where
moves: the total number of element moves to empty the queue
n: the number of items in the queue at the start
In words: each dequeue shifts everything still waiting, so the total grows with the square of the queue length: about half of n squared.
```

For 100,000 items that is about five billion moves, where a proper queue would do 100,000 cheap operations. That is O(n²) for the whole drain, or O(n) per dequeue. The bug is invisible in tests with 10 items and catastrophic in production with a million.

Two structures fix it: a linked list with head and tail pointers (dequeue at the head, enqueue at the tail, both O(1)), or, usually better, a **circular buffer**.

## Key takeaways
- A queue serves arrivals in their original order.
- Repeated list-front removal shifts a quadratic total of elements.

## Further reading
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
- [ArrayDeque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html)
