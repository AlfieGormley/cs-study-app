---
id: hash-collision-tombstones
title: Deletion, tombstones and rebuilding
level: intermediate
minutes: 3
sourceLesson: hash-collisions
summary: Deleting from an open-addressed table needs a tombstone (or shifting) so later keys stay reachable, and tombstones eventually force a rebuild.
---

An empty slot proves a search can stop only if insertion would also have stopped there. Deleting an intermediate entry must preserve that argument for entries further along the probe path.

## Deletion and tombstones

Deletion is where open addressing gets subtle. In the earlier seven-slot linear-probing example, keys 10, 17 and 24 (all homed at slot 3) occupy slots 3, 4 and 5. Suppose you delete 17 by setting slot 4 back to empty. A lookup for 24 starts at slot 3 (10, not a match), moves to slot 4, finds it empty, and concludes 24 is absent. Wrong: 24 sits in slot 5.

The fix is a **tombstone**: a special marker meaning "deleted, keep probing".

- **Lookups** skip over tombstones.
- **Inserts** may reuse the first tombstone they pass, but must still probe on to an empty slot to be sure the key is not already further along.

The two methods below are fragments of a table class. `EMPTY` and `TOMB` are unique marker objects, not stored keys, and `_probe(key)` yields the key's slot indices in probe order, at most one full cycle of the table:

```python
EMPTY, TOMB = object(), object()

def get(self, key):
    for i in self._probe(key):
        k = self.keys[i]
        # Only a never-used slot ends a
        # search.
        if k is EMPTY:
            raise KeyError(key)
        if k is not TOMB and k == key:
            return self.vals[i]
    raise KeyError(key)

def delete(self, key):
    for i in self._probe(key):
        k = self.keys[i]
        # Only a never-used slot ends a
        # search.
        if k is EMPTY:
            raise KeyError(key)
        if k is not TOMB and k == key:
            # Preserve later keys' probe
            # paths.
            self.keys[i] = TOMB
            return
    raise KeyError(key)
```

> [!warning] Tombstones pile up
> Tombstones count against the load for lookups, since searches must walk past them, but they hold no data. A table with heavy insert and delete churn can fill with tombstones, making misses slow even though it holds few live keys. Implementations track them and rebuild the table (rehash live keys into a fresh array) when they pass a threshold. In CPython 3.14 ordinary combined dicts, GIL-enabled builds can reuse dummy index slots; dense entry holes are generally compacted on rebuild. Free-threaded builds do not reuse dummy index slots, and popitem can trim the dense entry tail.

With linear probing there is an alternative: **backward-shift deletion**. After emptying a slot, scan forward and move back any key that could legally sit in the gap, until you reach an empty slot. No tombstones, at the cost of more work per delete.

## Follow the stopping proof

After deleting a key, ask what a future lookup will conclude at that slot. An empty marker says "no search ever needed to continue past here". A tombstone says "a search may once have continued past here, so keep going". Neither slot holds a live entry, but they make different promises.

The fragments also handle two edge cases. If the probe generator runs through a full cycle without meeting an empty slot, the key is absent, so both methods raise `KeyError` after the loop. A complete insert method, not shown, must update an existing key rather than blindly reuse the first tombstone it passes, and must cope with a table that has no truly empty slot left.

## Key takeaways
- An empty marker stops lookup; a tombstone does not.
- Insertion must keep searching for duplicates before reusing a tombstone.
- Deletion churn can require rebuilding even with few live keys.

## Further reading
- [Open addressing — Wikipedia](https://en.wikipedia.org/wiki/Open_addressing)
