---
id: hash-collision-linear-probes
title: Linear probing and clustering
level: intermediate
minutes: 4
sourceLesson: hash-collisions
summary: Linear probing steps to the next slot on a collision; clusters form, and miss cost rises steeply as the table fills.
---

Open addressing keeps every entry inside the slot array itself. Linear probing is its simplest form, and it shows the central trade-off of the whole family: excellent locality while the table has room, and a sharp slowdown as it fills.

## Open addressing

All keys live directly in the array, one per slot. To insert, you follow the key's **probe sequence**, a fixed list of slots to try in order (first choice, second choice, …), until you find an empty slot. A lookup follows the same sequence until it finds the key or hits an empty slot, which proves the key is absent: had it been inserted, it would have stopped there.

Because everything is in one contiguous array, open addressing is compact and cache-friendly. The load factor cannot exceed one: there are no more key positions than slots. Lookups for missing keys stop only at an empty slot, so these tables keep spare slots and grow well before they are full.

### Linear probing

Try the key's **home slot** (the slot its hash picks), then the next slot along, then the next, wrapping round from the end of the array to the start.

Example: a 7-slot table where each key's home slot is its remainder after dividing by 7. Insert 10, 17, 24, 3, 5 (home slots 3, 3, 3, 3, 5):

```
slot  0   1   2   3   4   5   6
      5   .   .   10  17  24  3
```

Four keys wanted slot 3 and spilled into 4, 5 and 6. Then 5, whose home was slot 5, found 5 and 6 taken and wrapped round to slot 0. Any key hashing anywhere into slots 3 to 6 now has to walk to the end of this run.

That is **primary clustering**: occupied runs grow, and a longer run is more likely to be hit and so grows faster. Runs that touch merge into even longer runs.

> [!analogy] Real-world analogy: parking along a single row
> Each driver is assigned a bay in a long row of numbered bays. If it is taken, they drive on to the next free bay. Early in the day everyone parks at or next to their bay. Late in the day, a block of full bays forms and every driver whose bay is in that block must crawl past it to the end.
>
> **How it maps:** bays are slots, the assigned bay is the home slot and driving on is the probe sequence. The full block is a cluster: the bigger it gets, the more drivers arrive inside it and lengthen it. Checking whether a friend has parked means walking from their bay until you find them or an empty bay.
>
> **Where it stops:** a real car park could put up a sign listing who is where. A hash table has only the slots themselves, and when a car leaves, its bay cannot simply be left empty without breaking other people's searches, which is the subject of the deletion lesson.

### How cost rises with load

Donald Knuth worked out how many slots linear probing examines on average. His formulas assume random, uniformly spread home slots, a large table, and keys that are only inserted (no deletions). In this model a hit costs roughly half of one over the fraction of slots still free, while a miss costs roughly half of one over the *square* of that fraction, so misses grow much faster as the table fills. That is why open-addressing tables resize long before they fill:

```formula reference
P_hit ≈ ½ × (1 + 1 / (1 − α))
P_miss ≈ ½ × (1 + 1 / (1 − α)^2)
where
P_hit: the expected number of slots examined by a successful search (key present)
P_miss: the expected number of slots examined by an unsuccessful search (key absent), which must reach an empty slot
α: alpha, the load factor: the fraction of slots occupied, between 0 and 1
½: one half
^: "to the power of"; (1 − α)^2 is (1 − α) multiplied by itself
≈: approximately equal to (the formulas are averages for large tables)
In words: everything depends on the fraction of slots still free. As it shrinks towards zero, a hit costs roughly half of one over that fraction and a miss roughly half of one over its square, so misses blow up first and fastest.
```

| Fullness | Hit | Miss |
|---|---|---|
| 50% | 1.5 | 2.5 |
| 75% | 2.5 | 8.5 |
| 90% | 5.5 | 50.5 |

Going from 75% full to 90% full makes the modelled miss cost about six times larger, while the hit cost only a little more than doubles. These are model averages, not timings: with tombstones from deletions, or patterned keys, real costs can be worse.

Despite clustering, linear probing often performs very well at moderate load, because consecutive slots usually sit in the same cache line and the processor fetches them together. Measure your implementation and workload rather than assuming either way.

## Key takeaways
- Linear probing continues into adjacent slots and wraps at the end.
- Occupied runs cause primary clustering.
- Knuth’s probe estimates concern a particular random insertion model without deletions.

## Further reading
- [Linear probing — Wikipedia](https://en.wikipedia.org/wiki/Linear_probing)
