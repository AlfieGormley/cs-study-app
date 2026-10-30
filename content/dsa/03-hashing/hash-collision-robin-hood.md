---
id: hash-collision-robin-hood
title: Robin Hood probe distances
level: intermediate
minutes: 3
sourceLesson: hash-collisions
summary: Robin Hood insertion gives a contested slot to the key that has travelled further, shrinking the worst probe distances and letting misses stop early.
---

Robin Hood hashing keeps linear probing's layout but changes who gets a contested slot. Its aim is not fewer collisions but a fairer spread of search lengths.

## Robin Hood hashing

Linear probing's average is fine, but its *variance* is the problem: some unlucky keys end up dozens of slots from home. Robin Hood hashing (Celis, Larson and Munro, 1985) evens this out by "taking from the rich and giving to the poor".

Each key's **probe distance** is how far it sits from its home slot, counting forward and wrapping round the end of the array. A key homed at slot 6 that ended up in slot 1 of an 8-slot table travelled 6 → 7 → 0 → 1: distance 3. A key in its home slot has distance 0, so it is "rich"; a key far from home is "poor".

While inserting, if the incoming key has travelled further than the resident of the current slot, they swap: the incoming key takes the slot and the displaced, "richer" key carries on probing.

The fragment below assumes the table has a free slot and the key is not already stored; a complete map must also handle updates to existing keys and grow before it fills.

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

> [!analogy] Real-world analogy: giving the seat to whoever has walked furthest
> Passengers board a long train and walk forward looking for a seat. The rule: if you reach a seat whose occupant has walked a shorter distance from their boarding door than you, you take it, and they get up and continue forward. The rule creates no extra seats, so the total walking stays the same, but the longest walks get shorter.
>
> **How it maps:** a passenger's boarding door is the home slot, distance walked is probe distance, and the swap is the Robin Hood rule. The total probe distance is shared out differently rather than reduced (with linear probing the set of occupied slots, and so the total, does not depend on who wins each swap): the longest distances shrink.
>
> **Where it stops:** passengers can see down the carriage; the table compares only with the one resident in the current slot. And if every key shares one home slot, the run is still long: the worst case remains linear.

Rust's standard `HashMap` used Robin Hood hashing until 2019 (Rust 1.36), when it switched to a Swiss-table design from the `hashbrown` crate.

## Key takeaways
- A more displaced incoming key takes a slot from a less displaced resident.
- The swap can reduce probe-distance variance while keeping linear adversarial worst cases.
- An absent-key search can stop at a resident with smaller distance.

## Further reading
- [Hash table: Robin Hood hashing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Robin_Hood_hashing)
