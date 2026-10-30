---
id: hash-resize-hysteresis-incremental
title: Growth increments, shrinking and pause limits
level: intermediate
minutes: 4
sourceLesson: hash-resizing
summary: Grow by a factor, shrink with a hysteresis gap, and use incremental rehashing when one long resize pause is unacceptable.
---

Geometric growth makes resizing cheap *on average*. This lesson covers three practical refinements: why the growth must be by a factor rather than a fixed amount, how to shrink without thrashing, and what to do when even one long pause is unacceptable.

## Fixed increments versus geometric growth

Growing by a constant **amount** does not work. Add 10 slots each time and every resize copies 10 more keys than the last. For n keys there is a resize every 10 inserts, and the later ones each copy most of the table, so the total copying grows with the square of n and the cost per insert keeps rising as the table grows: O(n) amortised rather than O(1). The program below counts the copies exactly for both policies:

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

Doubling copies 1,023 keys for 1,000 inserts, about one each; adding 10 slots at a time copies 49,600, about 50 each, and that per-insert figure keeps climbing as n grows.

> [!note] The banker's view
> Charge each insert 3 units instead of 1. One pays for the insert itself; two are saved. Between doublings, half the old capacity in new inserts earns two saved units per insert: enough to pay for moving every key in the full old table. No operation ever runs up a debt, so the average stays at 3.

### Shrinking without thrashing

If a table also shrinks when it empties, do not use the same threshold in both directions. Grow when the table is completely full and shrink when it drops below half full, and a workload hovering at the boundary (insert, delete, insert, …) would resize on every operation: a doubled table is exactly half full, so one delete shrinks it, and the shrunken table is full, so one insert doubles it again.

The textbook fix is a **hysteresis gap** (a deliberate difference between the grow and shrink points): double when full, halve only when the table falls to a quarter full. After either resize the table is half full, so at least a quarter of its size in operations must happen before the next one, and those cheap operations pay for it. Many real tables simply never shrink automatically; CPython's dict does not shrink when you delete keys.

> [!analogy] Real-world analogy: a thermostat
> A heating thermostat set to switch on below 19 °C and off above 21 °C does not flick on and off every few seconds when the room sits at 20 °C. If on and off shared a single setting, it would chatter constantly.
>
> **How it maps:** the room temperature is the load factor, switching the heating on or off is growing or shrinking the table, and the gap between 19 °C and 21 °C is the gap between the "full" and "quarter full" thresholds.
>
> **Where it stops:** a thermostat's switching is cheap and the room changes slowly. A resize costs work proportional to the whole table, so the gap must be wide enough that the operations between resizes can pay for that work, which is why the shrink point is a quarter, not just below a half.

### When amortised is not good enough

Amortised O(1) still means an occasional O(n) pause. The pause depends on the implementation, key count, allocator and hardware; measure it against the server's latency budget.

**Incremental rehashing** spreads the work out. Redis keeps two tables during a resize and moves a few buckets on each operation (plus, by default, a little extra work from its periodic housekeeping timer). Lookups check both tables until the move completes. Go's built-in map used a similar gradual "evacuation" before its Go 1.24 redesign. The cost is complexity and, temporarily, retaining both bucket arrays: when doubling, the old array plus one twice its size, so three times the old bucket count (excluding entries and other overhead).

If you know the final size, the simplest fix is to **pre-size** the table to avoid growth for the planned live-key count. Deletion churn can still require compaction/rebuilds.

## Key takeaways
- Fixed capacity increments cause growing amortised copying costs.
- Different grow and shrink thresholds prevent boundary thrashing.
- Incremental migration spreads pauses while temporarily retaining two tables.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
