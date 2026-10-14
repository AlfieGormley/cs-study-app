---
id: hash-collision-linear-probes
title: Linear probing and clustering
level: intermediate
minutes: 4
sourceLesson: hash-collisions
summary: Open addressing keeps entries inside the slot array.
---

Open addressing keeps entries inside the slot array. This unit uses linear probing and separates a table trace from Knuth’s large-table average model; the trace is exact, while the expected probe formulas rely on their stated assumptions.

## Open addressing

All keys live directly in the array, one per slot. To insert, you follow the key's **probe sequence**, a fixed list of slots to try in order (first choice, second choice, …), until you find an empty slot. A lookup follows the same sequence until it finds the key or hits an empty slot (which proves the key is absent).

Because everything is in one contiguous array, open addressing is compact and cache-friendly. The load factor cannot exceed one: there are no more key positions than slots. A completely full table can still search with a bounded complete probe cycle, but has no room for a new key. Designs that stop misses only at an empty slot keep spare slots, and performance falls off sharply as fullness approaches one.

### Linear probing

Try the key's home slot, then the next slot along, then the next, wrapping round from the end of the array to the start:

```formula
h(k, i) = (h(k) + i) mod m
h(24, 2) = (3 + 2) mod 7 = 5
where
h(k, i): the slot tried on attempt number i for key k
h(k): the key's home slot, the first slot its ordinary hash picks; here h(24) = 24 mod 7 = 3
k: the key being inserted or looked up, here 24
i: the attempt number, counting from 0 (the home slot) upwards; here 2, the third try
m: the number of slots in the array, here 7
mod: "modulo", the remainder after division; it wraps the slot number back to 0 after the last slot
In words: on each failed attempt move one slot to the right, wrapping round at the end; key 24's third try (i = 2) is slot 5.
```

Example: a 7-slot table where each key's home slot is its remainder after dividing by 7. Insert 10, 17, 24, 3, 5 (home slots 3, 3, 3, 3, 5):

```
slot  0   1   2   3   4   5   6
      5   .   .   10  17  24  3
```

Four keys wanted slot 3 and spilled into 4, 5 and 6. Then 5, whose home was slot 5, found 5 and 6 taken and wrapped round to slot 0. Any key hashing anywhere into slots 3 to 6 now has to walk to the end of this run.

That is **primary clustering**: occupied runs grow, and a longer run is more likely to be hit and so grows faster.

Donald Knuth worked out how many slots linear probing examines on average. His formulas assume random, uniformly spread home slots, a large table, and keys that are only inserted (no deletions or tombstones):

```formula
P_hit ≈ ½ × (1 + 1 / (1 − α))
P_miss ≈ ½ × (1 + 1 / (1 − α)^2)
P_hit ≈ ½ × (1 + 1 / 0.25) = 2.5
P_miss ≈ ½ × (1 + 1 / 0.0625) = 8.5
where
P_hit: the expected number of slots examined by a successful search (key present)
P_miss: the expected number of slots examined by an unsuccessful search (key absent), which must reach an empty slot
α: alpha, the load factor: the fraction of slots occupied, between 0 and 1; here 0.75
½: one half
^: "to the power of"; (1 − α)^2 is (1 − α) multiplied by itself
≈: approximately equal to (the formulas are averages for large tables)
In words: as the table fills, 1 − α (the fraction of free slots) shrinks, and a miss costs roughly one over its square; at 75% full a hit takes about 2.5 probes and a miss about 8.5.
```

The same formulas at three loads:

| α | Hit | Miss |
|---|---|---|
| 0.50 | 1.5 | 2.5 |
| 0.75 | 2.5 | 8.5 |
| 0.90 | 5.5 | 50.5 |

Going from 75% full to 90% full makes the modelled miss cost about six times larger (50.5 ÷ 8.5 ≈ 5.9). This is a model, not a wall-clock benchmark.

Despite clustering, linear probing can perform well at moderate load because nearby probes benefit from locality; measure the implementation and workload.

## Key takeaways
- Linear probing continues into adjacent slots and wraps at the end.
- Occupied runs cause primary clustering.
- Knuth’s probe estimates concern a particular random insertion model without deletions.

## Further reading
- [Linear probing — Wikipedia](https://en.wikipedia.org/wiki/Linear_probing)
