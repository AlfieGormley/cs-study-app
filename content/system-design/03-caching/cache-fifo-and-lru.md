---
id: cache-fifo-and-lru
title: Trace FIFO and LRU eviction
level: intermediate
minutes: 3
summary: Implement constant-time LRU operations and explain why one-off scans pollute a recency-based cache.
sourceLesson: cache-eviction
---

A cache is smaller than the data behind it, so eventually it fills up. When a new item arrives and there is no room, the cache must choose an **eviction victim** to throw out. The rule it uses is the **eviction policy** (or replacement policy).

The goal is to evict the item least likely to be needed again soon. Nobody knows the future, so every policy is a guess based on the past. The best guess depends on the access pattern.

Eviction (removing items because memory is full) is different from **expiry** (removing items because their time is up). Most caches do both.

## FIFO: first in, first out

Evict the item that was inserted earliest, regardless of how often it has been used.

- Trivial to implement: a queue.
- Ignores popularity. A key read 10,000 times a second is evicted just as readily as one read once.

Variants such as **CLOCK** and **SIEVE** build on cheap queues and reference bits without maintaining exact recency order.

## LRU: least recently used

Evict the item that has gone longest without being accessed. The bet is temporal locality: what was used recently will be used again.

> [!analogy] Real-world analogy: the desk-side bookshelf
> A small shelf by your desk holds a few books. Each time you use one you put it back at the left end; when a new book needs space, the one at the far right, untouched for longest, goes back to the library.
>
> **How it maps:** The shelf is the cache, putting a book back at the left is moving a key to the most-recently-used end on every hit, and returning the far-right book is evicting the least recently used key. FIFO would instead return whichever book arrived first, however often you use it.
>
> **Where it stops:** A shelf's order is visible at a glance; a cache needs extra bookkeeping (a map plus a linked list) to know the order quickly. And one afternoon of browsing many new books once each would push out your favourites, which is exactly LRU's scan problem below.

The classic implementation combines a **hash map** (key to node) with a **doubly linked list** ordered by recency. Both get and put have expected/amortized O(1) cost with ordinary hash-table assumptions. O(1), read "order one" or constant time, means the work per operation does not grow with n, the number of keys in the cache: a cache of a million keys does a get as cheaply as a cache of ten.

```
 MRU                          LRU
 head <-> [D] <-> [A] <-> [C] <-> tail
           ^ just used      ^ evict next
```

This is an executable cache class; it prints nothing by itself. The later questions trace the keys it retains.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        # A hit becomes the newest entry.
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        # Inserts and updates become newest.
        self.data.move_to_end(key)
        if len(self.data) > self.cap:
            # Evict the oldest access.
            self.data.popitem(last=False)
```

### Where LRU breaks: scans

LRU has a famous weakness. A one-off **scan** (a batch job reading a million keys once) pushes every key to the front, flushing the genuinely hot items out. After the scan, the cache is full of data nobody will ask for again. This is called **cache pollution**.

> [!example] LRU and a scan
> Capacity 3, contents `[A, B, C]` with A and B read constantly. A report reads X, Y, Z once each. LRU now holds `[X, Y, Z]`, and the next reads of A and B both miss.

Defences include segmented LRU (new items must prove themselves before entering the protected segment), LRU-K, 2Q and ARC, all of which consider more than one access.

## Key takeaways
- FIFO evicts the oldest insertion; LRU evicts the least recent access and assumes temporal locality.
- A hash map plus a doubly linked list gives expected or amortised constant-time LRU operations.
- A scan can replace useful hot keys with one-off reads; policies that consider reuse can protect the hot set.

## Further reading
- [OrderedDict — Python documentation](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [Adaptive replacement cache — Wikipedia](https://en.wikipedia.org/wiki/Adaptive_replacement_cache)
