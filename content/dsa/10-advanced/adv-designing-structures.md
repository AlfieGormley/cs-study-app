---
id: adv-designing-structures
title: Designing data structures
level: intermediate
minutes: 14
summary: How to combine a hash map with a linked list or an array to get O(1) operations, worked through LRU caches, LFU caches and a set with O(1) getRandom.
---

Most "design a data structure" problems share one idea: **no single structure gives you every operation cheaply, so you glue two together**. Each structure covers the other's weakness, and the hard part is keeping them in sync.

A hash map offers expected O(1) lookup but does not automatically maintain sorted-key or access-recency order. Python dictionaries do preserve insertion order. A linked list keeps order and can splice in O(1), but finding a node is O(n). An array gives O(1) access by position, but deleting from the middle is O(n). Combine them and you can often get O(1) for everything.

The method:

1. List the operations and the cost each must have.
2. For each operation, ask what it needs: lookup by key, an ordering, access by position?
3. Pick a structure for each need, and decide what the hash map's values point at (a node, an index).
4. Write down the **invariants** that tie them together, and check every operation preserves them.

Complexities below assume constant-time key hashing/equality and word-sized values. Hash operations are expected amortised O(1), and dynamic-array append/pop can resize; these are not worst-case per-operation guarantees.

## LRU cache: hash map + doubly linked list

An LRU (least recently used) cache holds at most `cap` items. `get(key)` returns a value and marks it as recently used; `put(key, value)` inserts or updates, evicting the least recently used item when full. Both must be O(1).

- **Lookup by key** needs a hash map.
- **Ordering by recency**, with "move to front" and "remove oldest", needs a list we can splice in O(1).

So the map stores `key -> node`, and the nodes form a doubly linked list ordered from most to least recent.

```
map: {A: *, B: *, C: *}
            |     |     |
head <-> [B] <-> [A] <-> [C] <-> tail
 MRU                              LRU
```

Why **doubly** linked? To unlink a node you must update its predecessor's `next`. With only `next` pointers, finding the predecessor is O(n). The `prev` pointer makes removal O(1).

Why store the **key in the node**? When you evict the tail you must also delete it from the map, and the node is all you have.

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
        n.prev.next = n.next
        n.next.prev = n.prev

    def _push_front(self, n):
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
                lru = self.tail.prev
                self._unlink(lru)
                del self.map[lru.key]
            n = Node(key, val)
            self.map[key] = n
        self._push_front(n)
```

> [!tip] Sentinel nodes
> The dummy `head` and `tail` nodes mean every real node always has a real `prev` and `next`. That removes every "is this the first node?" special case, which is where most hand-written linked-list bugs live.

The invariant: **a key is in the map if and only if its node is in the list**, and list order is recency order. Every branch of `put` maintains it: an update moves an existing node, an insert adds to both, an eviction removes from both.

In practice you rarely write this by hand. Python's `OrderedDict` (with `move_to_end` and `popitem(last=False)`) and Java's `LinkedHashMap` (with `accessOrder = true` and an overridden `removeEldestEntry`) are exactly this structure. CPython's positive, bounded `functools.lru_cache` uses a dict plus a circular doubly linked list; the unbounded mode does not need recency eviction.

## LFU cache: hash map + buckets of lists

An LFU (least frequently used) cache evicts the key with the fewest accesses, breaking ties by evicting the least recently used of those. Again, `get` and `put` should be O(1).

A heap keyed by frequency would give O(log n). The O(1) trick is to notice that **a frequency only ever goes up by one**. So instead of sorting, keep a bucket for each frequency:

- `val`: key to value.
- `freq`: key to its access count.
- `by_f`: count to an ordered set of keys with that count, oldest first.
- `min_f`: the smallest count currently present.

```
min_f = 1
by_f[1]: D -> E       (D older)
by_f[2]: B
by_f[5]: A -> C
evict: oldest in by_f[min_f] = D
```

When a key is touched, it moves from bucket `f` to bucket `f + 1`. If bucket `f` empties and `f` was the minimum, the new minimum is `f + 1`, because the key we just moved has exactly that count. When a new key is inserted, `min_f` resets to 1. That is why we never need to search for the minimum.

```python
from collections import defaultdict
from collections import OrderedDict

class LFUCache:
    def __init__(self, cap):
        self.cap = cap  # assume cap >= 0
        self.val = {}   # key -> value
        self.freq = {}  # key -> use count
        # count -> keys, oldest first
        self.by_f = defaultdict(OrderedDict)
        self.min_f = 0

    def _bump(self, key):
        f = self.freq[key]
        del self.by_f[f][key]
        if not self.by_f[f]:
            del self.by_f[f]
            if self.min_f == f:
                self.min_f = f + 1
        self.freq[key] = f + 1
        self.by_f[f + 1][key] = None

    def get(self, key):
        if key not in self.val:
            return -1
        self._bump(key)
        return self.val[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.val:
            self.val[key] = value
            self._bump(key)
            return
        if len(self.val) == self.cap:
            g = self.by_f[self.min_f]
            old, _ = g.popitem(last=False)
            if not g:
                del self.by_f[self.min_f]
            del self.val[old]
            del self.freq[old]
        self.val[key] = value
        self.freq[key] = 1
        self.by_f[1][key] = None
        self.min_f = 1
```

> [!warning] Evict before you insert
> In `put`, evict first and only then add the new key. If you insert first, `min_f` becomes 1 and the new key may be the only member of bucket 1. Evicting "the oldest key in the minimum bucket" then throws away the key you just added, while a stale key with count 2 survives.

Production caches seldom use exact LFU. Counts never decay in this design, so a formerly popular key can linger long after its usefulness ends. Redis uses an approximate, decaying 8-bit counter instead, and Caffeine uses a frequency sketch.

## Insert, delete and getRandom in O(1)

Design a set supporting `insert(x)`, `remove(x)` and `get_random()` (each element equally likely), all in O(1) average.

- A hash set gives O(1) insert and remove, but no way to pick a uniform random element without walking it.
- An array gives O(1) uniform random choice (`items[randrange(n)]`), but removing from the middle is O(n).

Combine them: an array of values plus a map from **value to index**. The clever step is deletion. Instead of shifting everything left, **move the last element into the hole** and pop the end, which is O(1).

```
remove(20)
items: [10, 20, 30, 40]   pos[20] = 1
copy last (40) into index 1
items: [10, 40, 30, 40]   pos[40] = 1
pop end, delete pos[20]
items: [10, 40, 30]
```

```python
import random

class RandomizedSet:
    def __init__(self):
        self.items = []  # the values
        self.pos = {}    # value -> index

    def insert(self, x):
        if x in self.pos:
            return False
        self.pos[x] = len(self.items)
        self.items.append(x)
        return True

    def remove(self, x):
        if x not in self.pos:
            return False
        i = self.pos[x]
        last = self.items[-1]
        self.items[i] = last  # overwrite x
        self.pos[last] = i
        self.items.pop()
        del self.pos[x]
        return True

    def get_random(self):
        return random.choice(self.items)
```

The order of the last two map operations matters. If `x` is itself the last element, `last == x`: we set `pos[x] = i` and then delete `pos[x]`, which is correct. Do it the other way round (delete, then set `pos[last]`) and you resurrect a map entry for a value that is no longer in the array.

`get_random()` requires a non-empty set; Python raises `IndexError` on an empty one.

The array does not preserve insertion order after a removal. That is fine here because a set has no order, but it is the price of O(1) deletion.

**With duplicates** (a multiset), map each value to a *set of indices*. Removal picks any index of `x`, moves the last element there, and updates the last element's index set. Now `get_random` returns each value with probability proportional to its count, which is usually what is wanted.

## Recognising the pattern

| Need | Structure |
|---|---|
| Find by key | Hash map |
| Recency or insertion order | Doubly linked list |
| Uniform random / by index | Dynamic array |
| Min or max, changing | Heap |
| Sorted order, ranges | Balanced BST |

Other classics built the same way:

- **Min stack**: a stack of `(value, min so far)` pairs gives O(1) `get_min`.
- **Time-based key-value store**: map from key to a list of `(timestamp, value)` appended in time order, then binary search, for O(log n) "value at time t".
- **All O(1) data structure** (increment, decrement, get max key, get min key): the LFU bucket idea, with a doubly linked list of count buckets.

## Pitfalls

- **Forgetting one side.** Every bug in these designs is the two structures drifting apart: a key left in the map after its node was evicted, or an index pointing at a moved element.
- **Average, not worst case.** The O(1) relies on hash map operations being O(1) on average. Adversarial keys can degrade them.
- **Capacity edge cases.** Capacity 0, updating an existing key when full (no eviction should happen), and removing the last element are where interview solutions break.
- **Concurrency.** A cache-hit `get` on this LRU implementation writes recency pointers. Concurrent access needs a correct synchronisation strategy, commonly a lock around operations; a miss does not move a node. This is one reason high-throughput caches approximate LRU instead.

## Key takeaways
- When no single structure supports every operation cheaply, combine two and keep an explicit invariant between them.
- LRU: hash map to nodes of a doubly linked list; the `prev` pointer makes unlinking O(1), and nodes store their key so eviction can clean the map.
- LFU in O(1): buckets keyed by frequency plus a `min_f` that only resets to 1 on insert or moves up by one.
- O(1) delete from an array: swap the last element into the hole and pop, updating its index in the map.
- Test the edge cases: capacity 0, updating when full, and removing the last element.

## Further reading
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [functools.lru_cache — Python docs](https://docs.python.org/3/library/functools.html)
- [LinkedHashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)
