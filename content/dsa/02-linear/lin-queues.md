---
id: lin-queues
title: Queues and deques
level: advanced
minutes: 14
summary: First-in, first-out queues and why a plain array makes a bad one, circular buffers, double-ended queues, the queue at the heart of breadth-first search, monotonic deques, and a first look at priority queues.
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
moves = n × (n − 1) / 2
moves ≈ n^2 / 2
where
moves: the total number of element moves to empty the queue
n: the number of items in the queue at the start
≈: approximately equal to; for large n, n − 1 is about n
In words: each dequeue shifts everything still waiting, so the total grows with the square of the queue length.
```

For 100,000 items that is about 100,000² / 2 = 5 billion moves; a proper queue would do 100,000 cheap operations. That is O(n²) for the whole drain, or O(n) per dequeue. The bug is invisible in tests with 10 items and catastrophic in production with a million.

Two structures fix it: a linked list with head and tail pointers (dequeue at the head, enqueue at the tail, both O(1)), or, usually better, a **circular buffer**.

## Circular buffers

A **circular buffer** (ring buffer) is a fixed array whose end wraps round to its start. Track the index of the front (`head`) and the number of items (`count`). The next free slot at the back is `count` places after `head`, wrapping round to slot 0 when it runs off the end:

```formula
back = (head + count) mod capacity
where
back: the slot index where the next enqueued item is written
head: the slot index of the item at the front (the next to be dequeued)
count: how many items are in the buffer now
capacity: the number of slots in the array
mod: modulo: the remainder after dividing; 6 mod 4 = 2. It makes indices wrap round, so they always stay between 0 and capacity − 1. Python writes it %
In words: start at the front, step forward one slot per stored item, and wrap round to the start of the array when you pass the end.
```

With capacity 4, head 2 and count 1, the next item goes in (2 + 1) mod 4 = slot 3; the one after goes in (2 + 2) mod 4 = slot 0, back at the start. In Python this is `(head + count) % capacity`.

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
        i = n % self.cap
        self.buf[i] = x
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            raise IndexError("empty")
        h = self.head
        x = self.buf[h]
        self.buf[h] = None   # drop the ref
        self.head = (h + 1) % self.cap
        self.count -= 1
        return x
```

### Full or empty?

If you store `head` and `tail` indices instead of a count, `head == tail` is ambiguous: it is true both when the buffer is empty and when it is full. The usual fixes:

1. Keep a **count** (as above).
2. **Waste one slot**: declare the buffer full when `(tail + 1) % cap == head`, so a full buffer holds `cap − 1` items and `head == tail` can only mean empty.
3. Use ever-increasing head and tail counters and compare `tail - head` with the capacity, taking indices `% cap` only when touching the array.

Option 3 with a **power-of-two capacity** lets you replace `% cap` with a cheap **bit mask** `& (cap - 1)`. When the capacity is a power of two, the remainder is just the lowest bits of the counter, and a bitwise AND keeps exactly those bits:

```formula
i mod cap = i AND (cap − 1)
13 mod 8 = 13 AND 7 = 5
where
i: an ever-increasing head or tail counter
cap: the buffer capacity, which must be a power of two (2, 4, 8, 16, ...)
mod: modulo: the remainder after dividing by cap
AND: bitwise AND: compares two numbers bit by bit, keeping a 1 only where both have a 1. Written & in C, Java and Python
In words: for a power-of-two capacity, the remainder after dividing by the capacity is just the counter's lowest bits, which one cheap AND instruction extracts.
```

Worked through in binary: 13 is 1101 and 7 is 0111, so the AND keeps 0101, which is 5, the same as 13 mod 8. With a capacity that isn't a power of two, such as 6, the trick fails: 13 mod 6 = 1 but 13 AND 5 = 5. The Linux kernel's `kfifo` works this way.

### Growing and bounding

A ring buffer can grow like a dynamic array: allocate double the space and copy the items across in queue order, "unwrapping" them. Java ArrayDeque also grows a circular array, but OpenJDK 21 roughly doubles small buffers and grows larger ones by about 50%, with additional adjustments for required capacity.

Often you don't want it to grow. A bounded queue configured to block or reject producers provides **backpressure**: when consumers fall behind, producers block or are refused, instead of memory growing until the process dies. Audio drivers, network card receive rings and high-throughput designs like the LMAX Disruptor all use fixed-size rings.

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
- **C++'s `std::deque`** uses an array of pointers to fixed-size chunks. It offers O(1) indexing as well as O(1) pushes at both ends.

### Bounded deques

`deque(maxlen=n)` keeps only the most recent n items. Appending to a full one silently discards an item from the **opposite** end. It's perfect for "the last 100 log lines" or a moving average.

```python
recent = deque(maxlen=3)
for x in [1, 2, 3, 4, 5]:
    recent.append(x)
print(recent)   # deque([3, 4, 5])
```

## Queues in BFS

**Breadth-first search** explores a graph in rings: all nodes one edge away, then two, then three. A queue enforces exactly that order, because nodes discovered earlier (closer) are processed before nodes discovered later (further).

```python
from collections import deque

def bfs(graph, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        node = q.popleft()
        for nb in graph[node]:
            if nb not in dist:
                dist[nb] = dist[node] + 1
                q.append(nb)
    return dist
```

In an **unweighted** graph, `dist` is the shortest number of edges from `start` to every reachable node. Replacing the queue with a stack removes the shortest-path guarantee. With discovery marked on push, it is a LIFO traversal but does not necessarily reproduce recursive DFS discovery/parent order; standard DFS uses an appropriate marking or iterator-stack strategy. Graph traversal gets a full treatment in the graphs module.

> [!warning] Mark nodes when you enqueue them
> Mark a node as seen when it's **added** to the queue, not when it's removed. Otherwise the same node can be enqueued many times by different neighbours, blowing up time and memory on dense graphs.

## Monotonic deques: sliding window maximum

Given an array of n numbers and a window size k, find the maximum of every run of k consecutive numbers (each run is a **sliding window**). Recomputing each window from scratch looks at k numbers for each of about n windows, O(nk). A **monotonic deque** does it in O(n).

Keep indices in the deque with their values **decreasing** from front to back. The front is always the current window's maximum.

```python
def window_max(nums, k):
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be >= 1")
    dq, out = deque(), []
    for i, x in enumerate(nums):
        # smaller values can never win again
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:   # left window
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
# [3, 3, 5, 5, 6, 7]
```

Values are removed from the **back** when a bigger value arrives (they're dominated: older *and* smaller) and from the **front** when they slide out of the window. Each index enters and leaves once, so the whole run is O(n), the same amortised argument as the monotonic stack.

## Priority queues

Sometimes "first come, first served" is wrong. An emergency department treats the most urgent patient first; an OS scheduler runs the highest-priority thread. A **priority queue** always removes the item with the **best priority** (smallest or largest key), whenever it arrived.

For a queue holding n items, simple implementations make one operation slow. In the table, log n means log₂ n, the number of times n can be halved before reaching 1: about 20 for a million items, so O(log n) operations stay cheap even for huge queues.

| Implementation | insert | remove-min |
|---|---|---|
| Unsorted array | O(1) | O(n) |
| Sorted array | O(n) | O(1) |
| Binary heap | O(log n) | O(log n) |

The **binary heap** balances both, and also gives O(1) peek and O(n) construction from an existing list. How it works (a tree packed into an array) is covered in the heaps module; for now, use the library.

```python
import heapq
h = []
heapq.heappush(h, (2, "write report"))
heapq.heappush(h, (1, "fix outage"))
heapq.heappush(h, (3, "lunch"))
heapq.heappop(h)  # (1, 'fix outage')
```

Practical details:

- The traditional heapq functions use a min-heap on a list. Python 3.14 adds public max-heap functions such as heappush_max and heappop_max; on older versions, negate numeric keys.
- With `(priority, item)` tuples, equal priorities fall back to comparing the items, which fails with a `TypeError` for dicts and other non-comparable objects (and, for comparable items, silently orders ties by the item rather than by arrival). Add a counter: `(priority, next(counter), item)`.
- Java's `PriorityQueue` is also a min-heap by default; pass a `Comparator` for other orders. Its iterator does **not** visit items in priority order.
- Uses include Dijkstra's shortest paths, event-driven simulations, schedulers, merging k sorted lists and keeping the top k items.

## Key takeaways
- A queue is FIFO; `list.pop(0)` makes dequeue O(n) for n queued items, so use `collections.deque` or a ring buffer.
- A circular buffer wraps indices modulo capacity; disambiguate full from empty with a count or a wasted slot.
- Bounded queues give backpressure; unbounded ones turn slow consumers into memory exhaustion.
- Deques give O(1) at both ends; Python's is block-linked, Java's `ArrayDeque` is a circular array.
- BFS's queue processes nodes in order of distance, giving shortest paths in unweighted graphs; mark nodes seen on enqueue.
- A priority queue serves the best key first; for n items a binary heap gives O(log n) insert and remove. In Python, use `heapq` with a tie-breaking counter.

## Further reading
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Double-ended queue — Wikipedia](https://en.wikipedia.org/wiki/Double-ended_queue)
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [ArrayDeque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Priority queue — Wikipedia](https://en.wikipedia.org/wiki/Priority_queue)
