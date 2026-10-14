---
id: hash-resize-hysteresis-incremental
title: Growth increments, shrinking and pause limits
level: intermediate
minutes: 4
sourceLesson: hash-resizing
summary: A constant average over a sequence does not constrain each individual pause.
---

A constant average over a sequence does not constrain each individual pause. This unit contrasts fixed increments, shrink hysteresis and gradual migration between two tables.

## Fixed increments versus geometric growth

Growing by a constant **amount** does not work. Add 10 slots each time and every resize copies 10 more keys than the last:

```formula
C ≈ 10 + 20 + 30 + … + n
C ≈ n^2 / 20
C ≈ 1000^2 / 20 = 50,000
where
C: the total number of key copies made by all the resizes
n: the number of keys inserted, here 1,000
…: "and so on", each term 10 more than the one before
^: "to the power of"; n^2 = n × n
≈: approximately equal to
In words: an arithmetic series of about n/10 resizes, averaging n/2 copies each, totals about n²/20; for 1,000 keys that is around 50,000 copies, about 50 per insert, and the per-insert cost keeps growing with n.
```

That is O(n) per insert, amortised. The program below counts the copies exactly (it starts at one slot, so its numbers differ slightly from the formula):

```python
def total_copies(n, grow):
    cap, size, copies = 1, 0, 0
    for _ in range(n):
        if size == cap:
            # Count only moves, not hash
            # work.
            copies += size
            cap = grow(cap)
        size += 1
    return copies

total_copies(1000, lambda c: 2 * c)
# 1023
total_copies(1000, lambda c: c + 10)
# 49600
```

> [!note] The banker's view
> Charge each insert 3 units instead of 1. One pays for the insert itself; two are saved. Between doublings, half the old capacity in new inserts earns two saved units per insert: enough to pay for moving every key in the full old table. No operation ever runs up a debt, so the average stays at 3.

### Shrinking without thrashing

If a table also shrinks when it empties, do not use the same threshold in both directions. Grow when the table is completely full (load factor 1) and shrink when it drops below half full (load factor ½), and a workload hovering at the boundary (insert, delete, insert, …) would resize on every operation: a doubled table is exactly half full, so one delete shrinks it, and the shrunken table is full, so one insert doubles it again. The textbook fix is a **hysteresis gap** (a deliberate difference between the grow and shrink points): double when full, halve only when the load factor falls to ¼. After either resize the table is half full, so at least a quarter of its size in operations must happen before the next one. Many real tables simply never shrink automatically; CPython's dict does not shrink when you delete keys.

### When amortised is not good enough

Amortised O(1) still means an occasional O(n) pause. The pause depends on the implementation, key count, allocator and hardware; measure it against the server's latency budget.

**Incremental rehashing** spreads the work out. Redis keeps two tables during a resize and moves a few buckets on each operation (plus a little work in a background timer). Lookups check both tables until the move completes. Go's built-in map used a similar gradual "evacuation" before its Go 1.24 redesign. The cost is complexity and, temporarily, retaining both bucket arrays: when doubling, the old array plus one twice its size, so three times the old bucket count (excluding entries and other overhead).

If you know the final size, the simplest fix is to **pre-size** the table to avoid growth for the planned live-key count. Deletion churn can still require compaction/rebuilds.

## Key takeaways
- Fixed capacity increments cause growing amortised copying costs.
- Different grow and shrink thresholds prevent boundary thrashing.
- Incremental migration spreads pauses while temporarily retaining two tables.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
