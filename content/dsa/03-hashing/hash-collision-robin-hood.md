---
id: hash-collision-robin-hood
title: Robin Hood probe distances
level: intermediate
minutes: 3
sourceLesson: hash-collisions
summary: Robin Hood insertion compares how far two keys have travelled.
---

Robin Hood insertion compares how far two keys have travelled. It changes which key keeps a contested slot, aiming to reduce variation in search lengths rather than eliminate collision costs.

## Robin Hood hashing

Linear probing's average is fine, but its *variance* is the problem: some unlucky keys end up dozens of slots from home. Robin Hood hashing (Celis, Larson and Munro, 1985) evens this out by "taking from the rich and giving to the poor".

The insertion fragment requires a nonempty table with a free slot and a key not already stored; a complete map must handle duplicate updates and grow before exhausting capacity. Each key's **probe distance** is how far it sits from its home slot, counting forward and wrapping round the end of the array:

```formula
d = (s − h) mod m
d = (1 − 6) mod 8 = 3
where
d: the probe distance, a whole number of slots (0 means the key sits in its home slot)
s: the slot the key actually occupies, here 1
h: the key's home slot, here 6
m: the number of slots, here 8
mod: "modulo", the remainder after division, taken as a value from 0 to m − 1 (so −5 mod 8 = 3)
In words: count how many steps forward the key had to travel from its home slot; a key homed at slot 6 that ended up in slot 1 of an 8-slot table travelled 6 → 7 → 0 → 1, a distance of 3.
```

While inserting, if the incoming key has travelled further than the resident of the current slot, they swap: the incoming key takes the slot and the displaced, "richer" key carries on probing.

```python
def rh_insert(slots, key, home):
    # slots hold (key, dist) or None
    m = len(slots)
    i, d = home % m, 0
    while True:
        cur = slots[i]
        if cur is None:
            slots[i] = (key, d)
            return
        # The more displaced key keeps the
        # slot.
        if cur[1] < d:  # resident richer
            slots[i] = (key, d)
            key, d = cur  # carry it on
        i = (i + 1) % m
        d += 1
```

Insert D (home 2), then A, B and C (all home 0):

```
plain linear    A0  B1  D0  C3
robin hood      A0  B1  C2  D1
               (key + probe distance)
```

C reaches slot 2 having travelled 2; D there has travelled 0, so C takes the slot and D moves on to slot 3. The total distance is the same (4), but the worst case drops from 3 to 2. Robin Hood hashing can reduce probe-distance variance; worst-case lookup remains O(n) under adversarial collisions.

It also speeds up misses. Probing for an absent key, you can stop as soon as you meet a resident whose distance is smaller than your current distance: had your key been present, it would have displaced that resident. Deletion usually uses backward shifting.

Rust's standard `HashMap` used Robin Hood hashing until 2019 (Rust 1.36), when it switched to a Swiss table.

## Key takeaways
- A more displaced incoming key takes a slot from a less displaced resident.
- The swap can reduce probe-distance variance while keeping linear adversarial worst cases.
- An absent-key search can stop at a resident with smaller distance.

## Further reading
- [Hash table: Robin Hood hashing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Robin_Hood_hashing)
