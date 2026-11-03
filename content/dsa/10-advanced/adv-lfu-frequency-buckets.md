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

An indexed min-heap could put the least-used key at the top, but a hit changes its count and may require O(log n) work to restore heap order, where n is the number of cached keys. A key-to-heap-position map would also be needed to locate the entry quickly.

The constant-time trick is that **a frequency only ever goes up by one**. Keep a bucket for each frequency:

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

When a touched key leaves the lowest bucket empty, the next bucket becomes the minimum: the touched key has just entered it. A new key starts at count one and resets `min_f` to one. Neither operation needs to search for the next occupied bucket.

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
- [Constant-time LFU design — Shah, Mitra and Matani](https://arxiv.org/pdf/2110.11602)
- [Python ordered dictionaries](https://docs.python.org/3/library/collections.html)
- [Redis cache eviction policies](https://redis.io/docs/latest/develop/reference/eviction/)
