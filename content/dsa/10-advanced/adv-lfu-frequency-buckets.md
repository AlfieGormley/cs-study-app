---
id: adv-lfu-frequency-buckets
title: LFU caches and frequency buckets
level: intermediate
minutes: 5
summary: Move an accessed key exactly one frequency bucket upwards.
sourceLesson: adv-designing-structures
---

## LFU cache: hash map + buckets of lists

An LFU (least frequently used) cache evicts the key with the fewest accesses, breaking ties by evicting the least recently used of those. Again, `get` and `put` should be O(1).

The obvious design is a min-heap of keys ordered by count, so the least-used key sits at the top. The catch is that every `get` raises a count, and the heap must then sift that key to its new place:

```formula
s_heap = O(log_2(n))
h_heap = ⌊log_2(n)⌋
h_heap = ⌊log_2(10^6)⌋ = 19
where
s_heap: an upper bound on work to restore heap order after one key’s count changes
h_heap: the maximum root-to-leaf path length in edges, bounding swaps for this binary heap
⌊ ⌋: floor, rounding down to a whole number
n: the number of keys in the cache; here one million (10^6)
log_2(n): the base-2 logarithm of n: how many times n can be halved before reaching 1, which is about the height of the heap
O(f): big-O notation: the step count grows no faster than f as n grows, ignoring constant factors
≈: approximately equal to
In words: with a heap, every access costs a number of swaps that grows with the logarithm of the cache size, at most 19 swaps for a million keys, plus comparisons, instead of a fixed handful.
```

At most nineteen swaps is not much, but it is not O(1), and some hits require no swaps at all. The O(1) trick is to notice that **a frequency only ever goes up by one**. So instead of sorting, keep a bucket for each frequency:

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

When a key is touched, its count goes up by exactly one, so it moves to the next bucket up. Two update rules keep `min_f` correct without ever searching:

```formula
c_k ← f + 1
min_f ← f + 1   if |B_f| = 0 and min_f = f
min_f ← 1       if f = 0
where
k: the key being touched (read or written)
f: k's access count just before this touch; 0 for a key that is being inserted for the first time
c_k: k's access count after the touch (1 for a newly inserted key)
B_f: the bucket of keys whose count is exactly f, oldest first
|B_f|: the number of keys left in bucket B_f after k has moved out
min_f: the smallest access count any key in the cache currently has
←: "is set to": the left side takes the value on the right
In words: a touched key moves up one bucket; if that empties the lowest bucket, the new lowest is the bucket the key just moved into, and a brand-new key (count 1) always makes 1 the lowest.
```

Worked example, using the bucket picture above: touch D, whose count f is 1. D moves to bucket 2, but bucket 1 still holds E, so `min_f` stays 1. Now touch E: bucket 1 empties and `min_f` was 1, so `min_f` becomes 2, and bucket 2 is guaranteed non-empty because E has just landed in it. No smaller bucket can be non-empty, because `min_f` was the smallest. The rules rely on counts only rising by one at a time; a design that could decrement or reset counts would need a real search.

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
        # Move only this key to the next
        # count.
        f = self.freq[key]
        del self.by_f[f][key]
        if not self.by_f[f]:
            del self.by_f[f]
            if self.min_f == f:
                # The moved key fills the
                # next bucket.
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
            # Oldest key breaks equal-count
            # ties.
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

## Key takeaways

- Move an accessed key exactly one frequency bucket upwards.
- An emptied minimum bucket advances by one because the touched key just entered that next bucket.

## Further reading
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [functools.lru_cache — Python docs](https://docs.python.org/3/library/functools.html)
- [LinkedHashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)
- [Constant-time LFU design paper](https://arxiv.org/pdf/2110.11602)
