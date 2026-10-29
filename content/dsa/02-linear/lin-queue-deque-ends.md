---
id: lin-queue-deque-ends
title: Deques, block layouts and bounded histories
level: advanced
minutes: 3
sourceLesson: lin-queues
summary: A deque supports both ends; its middle-access cost depends on implementation.
---

A queue adds at one end and removes at the other. A deque allows either operation at either end. Here n is the number of stored items; bounds concern container operations, excluding user-defined finalisers or other work triggered by dropping an object.

## Deques: both ends

A **deque** (double-ended queue, pronounced "deck") supports O(1) insertion and removal at **both** ends. It can act as a stack, a queue, or both at once.

For a deque holding n items:

| Python `collections.deque` | Cost |
|---|---|
| `append(x)`, `appendleft(x)` | O(1) |
| `pop()`, `popleft()` | O(1) |
| `d[0]`, `d[-1]` | O(1) |
| `d[i]` in the middle | O(n) |

```python
from collections import deque
d = deque([2, 3])
d.appendleft(1)   # [1, 2, 3]
d.append(4)       # [1, 2, 3, 4]
d.popleft()       # 1
d.pop()           # 4
```

How it's built varies:

- **CPython's `deque`** is a doubly linked list of fixed-size blocks (64 items each), so both ends are O(1) with no resizing, and access near the middle is O(n). Its docs note that appends and pops from either end are thread-safe.
- **Java's `ArrayDeque`** is a growable circular array. It's the recommended general-purpose queue and stack in Java, and usually faster than `LinkedList`.
- **C++'s `std::deque`** is typically implemented as an array of pointers to fixed-size chunks. The standard guarantees constant-time indexing (random-access iterators) as well as constant-time insertion and removal at both ends.

### Bounded deques

`deque(maxlen=n)` keeps only the most recent n items. Appending to a full one silently discards an item from the **opposite** end. It's perfect for "the last 100 log lines" or a moving average.

```python
recent = deque(maxlen=3)
for x in [1, 2, 3, 4, 5]:
    recent.append(x)
# Keeps only the three newest values.
# deque([3, 4, 5], maxlen=3)
print(recent)
```

### A bounded history differs from a bounded work queue

A deque with a positive maxlen is an eviction policy: a full append removes the oldest item at the opposite end. It does not wait for a consumer to make room. A Queue with maxsize is a coordination policy: a blocking put waits when the queue is full.

For the five successive values one through five and a three-item history, the retained values are three, four and five. Adding zero at the left then discards five at the right, leaving zero, three and four. Choose maxlen for recent context that may be discarded, rather than work items that must all be processed.

Thread-safe individual deque appends and pops do not make a multi-step check-then-pop protocol atomic. Between checking nonemptiness and popping, another thread could remove the last item. Use a coordinating queue or an explicit lock when several operations form one protocol.

## Key takeaways
- A deque supports both ends; its middle-access cost depends on implementation.
- A maxlen history evicts from the opposite end instead of blocking producers.

## Further reading
- [Double-ended queue — Wikipedia](https://en.wikipedia.org/wiki/Double-ended_queue)
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
- [ArrayDeque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html)
