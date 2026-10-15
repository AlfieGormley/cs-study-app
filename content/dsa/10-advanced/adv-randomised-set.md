---
id: adv-randomised-set
title: Random choice with constant-time deletion
level: intermediate
minutes: 3
summary: Swap the last array item into a deleted slot and repair its map index.
sourceLesson: adv-designing-structures
---

## Insert, delete and getRandom in O(1)

Design a set supporting `insert(x)`, `remove(x)` and `get_random()` (each element equally likely), all in O(1) average.

- A hash set gives O(1) insert and remove, but no way to pick a uniform random element without walking it.
- An array gives O(1) uniform random choice (`items[randrange(n)]`), but removing from the middle is O(n), where n is the number of elements, because every later element shifts left.

Combine them: an array of values plus a map from value to index. The clever step is deletion. Instead of shifting everything left, **move the last element into the hole** and pop the end, which is O(1).

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
        # Repair the moved value’s lookup
        # index.
        self.pos[last] = i
        self.items.pop()
        # Delete after repair, even if x is
        # last.
        del self.pos[x]
        return True

    def get_random(self):
        return random.choice(self.items)
```

The order of the last two map operations matters. If `x` is itself the last element, `last == x`: we set `pos[x] = i` and then delete `pos[x]`, which is correct. Do it the other way round (delete, then set `pos[last]`) and you resurrect a map entry for a value that is no longer in the array.

`get_random()` requires a non-empty set; Python raises `IndexError` on an empty one.

The array does not preserve insertion order after a removal. That is fine here because a set has no order, but it is the price of O(1) deletion.

With duplicates (a multiset), map each value to a *set of indices*. Removal picks any index of `x`, moves the last element there, and updates the last element's index set. `get_random` still picks one array slot uniformly, so a value that fills more slots comes up more often:

```formula
P(v) = c_v / n
P(1) = 2 / 3 ≈ 0.67
where
v: one of the values stored in the multiset
P(v): the probability that get_random returns v, from 0 (never) to 1 (always)
c_v: the number of copies of v in the array
n: the total number of elements in the array, counting every copy
≈: approximately equal to
In words: each value's chance of being picked is its share of the array's slots.
```

For `items = [1, 1, 2]`, the value 1 has 2 copies out of 3 slots, so it is returned about two times in three and 2 about one time in three. Returning each value with probability proportional to its count is usually what is wanted from a multiset; if you need each *distinct* value equally often, you need a separate array of distinct values to sample from.

## Key takeaways

- Swap the last array item into a deleted slot and repair its map index.
- Sampling array slots weights duplicate values by their number of copies.

## Further reading
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [functools.lru_cache — Python docs](https://docs.python.org/3/library/functools.html)
- [LinkedHashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)
