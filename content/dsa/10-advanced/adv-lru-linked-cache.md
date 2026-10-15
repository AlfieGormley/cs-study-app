---
id: adv-lru-linked-cache
title: LRU caches and recency pointers
level: intermediate
minutes: 3
summary: A key-to-node lookup reaches the matching recency-list node.
sourceLesson: adv-designing-structures
---

## LRU cache: hash map + doubly linked list

An LRU (least recently used) cache holds at most `cap` items. `get(key)` returns a value and marks it as recently used; `put(key, value)` inserts or updates, evicting the least recently used item when full. Both must be O(1).

- Lookup by key needs a hash map.
- Ordering by recency, with "move to front" and "remove oldest", needs a list we can splice in O(1).

So the map stores `key -> node`, and the nodes form a doubly linked list ordered from most to least recent.

```
map: {A: *, B: *, C: *}
            |     |     |
head <-> [B] <-> [A] <-> [C] <-> tail
 MRU                              LRU
```

Why doubly linked? To unlink a node you must update its predecessor's `next`. With only `next` pointers, finding the predecessor is O(n), where n is the number of nodes in the list, because you must walk from the head. The `prev` pointer makes removal O(1).

Why store the key in the node? When you evict the tail you must also delete it from the map, and the node is all you have.

```python
class Node:
    def __init__(self, key=None, val=None):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, cap):
        self.cap = cap   # assume cap >= 1
        self.map = {}    # key -> Node
        self.head = Node()  # MRU sentinel
        self.tail = Node()  # LRU sentinel
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, n):
        # Bypass n in both neighbouring
        # links.
        n.prev.next = n.next
        n.next.prev = n.prev

    def _push_front(self, n):
        # Insert just after the MRU
        # sentinel.
        first = self.head.next
        n.prev, n.next = self.head, first
        first.prev = n
        self.head.next = n

    def get(self, key):
        n = self.map.get(key)
        if n is None:
            return -1
        self._unlink(n)
        self._push_front(n)
        return n.val

    def put(self, key, val):
        n = self.map.get(key)
        if n is not None:
            n.val = val
            self._unlink(n)
        else:
            if len(self.map) == self.cap:
                # Evict the oldest real
                # node, not tail.
                lru = self.tail.prev
                self._unlink(lru)
                # Remove the evicted key
                # from lookup too.
                del self.map[lru.key]
            n = Node(key, val)
            self.map[key] = n
        self._push_front(n)
```

> [!tip] Sentinel nodes
> The dummy `head` and `tail` nodes mean every real node always has a real `prev` and `next`. That removes every "is this the first node?" special case, which is where most hand-written linked-list bugs live.

The invariant: **a key is in the map if and only if its node is in the list**, and list order is recency order. Every branch of `put` maintains it: an update moves an existing node, an insert adds to both, an eviction removes from both.

In practice you rarely write this by hand. Python's `OrderedDict` (with `move_to_end` and `popitem(last=False)`) and Java's `LinkedHashMap` (with `accessOrder = true` and an overridden `removeEldestEntry`) are exactly this structure. CPython's positive, bounded `functools.lru_cache` uses a dict plus a circular doubly linked list; the unbounded mode does not need recency eviction.

## Key takeaways

- A key-to-node lookup reaches the matching recency-list node.
- Unlink and relink on hits; eviction removes a node from both structures.

## Further reading
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [functools.lru_cache — Python docs](https://docs.python.org/3/library/functools.html)
- [LinkedHashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)
- [CPython 3.14 cache implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/functools.py)
