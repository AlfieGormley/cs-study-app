---
id: hash-collision-quadratic-double
title: Quadratic probing and double hashing
level: intermediate
minutes: 5
sourceLesson: hash-collisions
summary: Quadratic probing and double hashing break up clusters, but table size and step choice decide whether every slot can be reached.
---

Linear probing's clusters come from every colliding key taking the same one-slot steps. The fixes in this lesson change the step pattern. But a probe sequence must do more than spread collisions: it must be able to reach a free slot, and the table size and step pattern together decide whether it can.

## Quadratic probing

Instead of stepping one slot at a time, jump by growing amounts: successive retries land 1, 4, 9, 16, … slots from home (the squares), wrapping round the array. Runs no longer merge so readily.

```formula reference
h(k, i) = (h(k) + c_1 i + c_2 i^2) mod m
where
h(k, i): the slot tried on attempt i for key k
h(k): the key's home slot
k: the key being placed or looked up
i: the attempt number, counting from 0
c_1: a fixed constant multiplying the attempt number (0 in the plain "i squared" version)
c_2: a fixed non-zero constant multiplying the attempt number squared (1 in the plain version)
m: the number of slots
mod: "modulo", the remainder after division, which wraps round the array
^: "to the power of"; i^2 = i × i
In words: the distance from home grows with the square of the attempt number, so successive retries spread further and further apart.
```

This removes primary clustering but leaves **secondary clustering**: keys with the same home slot still follow the identical sequence.

Quadratic probing also may not visit every slot. In a 7-slot table, a key homed at slot 0 tries 0, 1, 4, 2, 2, 4, 1, 0, … and never reaches slots 3, 5 or 6. There is a useful guarantee, though: when the number of slots is an odd prime, the first half (rounded up) of the squared-offset probes are all different. So if the table is less than half full, one of those probes must be free and the insert succeeds. Arbitrary choices of the constants have no such guarantee.

A popular variant steps by **triangular numbers** (0, 1, 3, 6, 10, …, each one more step than the last), which visits every slot exactly once when the table size is a power of two. In an 8-slot table those offsets land on slots 0, 1, 3, 6, 2, 7, 5, 4: all eight.

### Double hashing

Use a second hash to choose each key's step size. Each retry moves one more step of that size from home, wrapping round:

```formula reference
h(k, i) = (h_1(k) + i h_2(k)) mod m
where
h(k, i): the slot tried on attempt i for key k
h_1(k): the first hash, giving the home slot
h_2(k): the second hash, giving this key's step size
k: the key
i: the attempt number, counting from 0
m: the number of slots
mod: "modulo", the remainder after division
In words: start at the home slot and move by a key-specific step on each failed attempt, wrapping round the array.
```

Keys with the same home slot now usually follow different sequences, reducing clustering when the two hashes distribute keys well; keys sharing both hashes still share a sequence. Two rules: the step must never be 0 (or you probe the same slot forever), and it must be **coprime** with the table size (share no factor with it other than 1) so the sequence can reach every slot. For a prime table size, any step that is not a multiple of it works; for a power-of-two size, any odd step works.

> [!analogy] Real-world analogy: guests searching a hotel corridor for a free room
> Hotel guests whose assigned room is taken all try the next door along, so they bunch up at the same few doors: that is linear probing. Double hashing gives each guest a personal jump length, say every third door or every fifth, so guests with the same first choice fan out.
>
> **How it maps:** the first-choice room is the home slot and the jump length is the second hash's step. A jump length that shares a factor with the number of doors, like every second door in a corridor of 16, only ever visits half the rooms, which is why the step must be coprime with the table size.
>
> **Where it stops:** a guest could simply read the vacancy board. A hash table has no board: the same jumps have to be retraced on every later lookup, so the step must be a fixed function of the key.

For the same keys as the linear-probing example (10, 17, 24, 3, 5 into 7 slots, home slot `k % 7`), use the step `5 - k % 5`, which is always between 1 and 5:

```
slot  0   1   2   3   4   5   6
      .   5   .   10  24  3   17
```

17 jumps 3 slots to slot 6, and 24 steps 1 slot to slot 4, rather than all queuing behind 10. The price is computing a second hash and losing the cache locality of linear steps.

## Key takeaways
- Quadratic sequences need table-size and coefficient conditions for coverage.
- Double hashing uses a nonzero step coprime to table size.
- Power-of-two tables need odd double-hash steps for complete coverage.

## Further reading
- [Open addressing — Wikipedia](https://en.wikipedia.org/wiki/Open_addressing)
- [Double hashing — Wikipedia](https://en.wikipedia.org/wiki/Double_hashing)
