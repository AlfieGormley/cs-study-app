---
id: adv-skiplist-search-insert
title: Searching and inserting in a skip list
level: advanced
minutes: 2
summary: Search moves right below the target, then drops down a level.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

### Search

Start at the top-left. Move right while the next key is smaller than the target. When you cannot, drop down a level. At level 1, the next node is the target if it is present.

```python
import random

class Node:
    def __init__(self, key, level):
        self.key = key
        self.next = [None] * level

class SkipList:
    MAX = 32
    P = 0.5

    def __init__(self):
        self.head = Node(None, self.MAX)
        self.level = 1

    def _random_level(self):
        lvl = 1
        while lvl < self.MAX:
            if random.random() >= self.P:
                break
            lvl += 1
        return lvl

    def search(self, key):
        x = self.head
        top = self.level
        for i in range(top - 1, -1, -1):
            while (x.next[i]
                   and x.next[i].key < key):
                x = x.next[i]
        x = x.next[0]
        if x is None:
            return False
        return x.key == key
```

### Insert

Search as usual, but remember the last node visited on each level (`update[i]`). Those are the nodes whose pointers must change. Then pick a random level and splice the new node in on each of its levels.

```python
    def insert(self, key):
        update = [self.head] * self.MAX
        x = self.head
        top = self.level
        for i in range(top - 1, -1, -1):
            while (x.next[i]
                   and x.next[i].key < key):
                x = x.next[i]
            # Save the predecessor on this
            # level.
            update[i] = x
        lvl = self._random_level()
        self.level = max(self.level, lvl)
        node = Node(key, lvl)
        for i in range(lvl):
            # Preserve the old successor
            # first.
            node.next[i] = update[i].next[i]
            # Then splice in the new tower
            # level.
            update[i].next[i] = node
```

This `insert` method continues the `SkipList` class from the search example. It permits duplicate keys; it is an ordered membership demonstration rather than a distinct-key set API.

Delete is symmetrical: find `update`, then unlink the node on each level it occupies. No rotations, no colour rules.

## Key takeaways

- Search moves right below the target, then drops down a level.
- Remember each level’s predecessor before splicing a new tower.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
