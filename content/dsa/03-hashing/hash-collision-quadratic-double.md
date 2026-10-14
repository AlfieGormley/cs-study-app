---
id: hash-collision-quadratic-double
title: Quadratic probing and double hashing
level: intermediate
minutes: 5
sourceLesson: hash-collisions
summary: A probe sequence must do more than spread collisions: it must reach a free slot.
---

A probe sequence must do more than spread collisions: it must reach a free slot. The table size and the step sequence together determine coverage.

## Quadratic probing

Jump by growing amounts so runs do not merge so readily:

```formula
h(k, i) = (h(k) + c_1 i + c_2 i^2) mod m
h(k, 3) = (0 + 0 × 3 + 1 × 9) mod 7 = 2
where
h(k, i): the slot tried on attempt i for key k
h(k): the key's home slot, here 0
k: the key being placed or looked up
i: the attempt number, counting from 0
c_1: a fixed constant multiplying the attempt number, here 0
c_2: a fixed non-zero constant multiplying the attempt number squared, here 1
m: the number of slots, here 7
mod: "modulo", the remainder after division, which wraps round the array
^: "to the power of"; i^2 = i × i
In words: the step from home grows with the square of the attempt number; with c_1 = 0 and c_2 = 1 in a 7-slot table, a key homed at slot 0 tries slots 0, 1, 4, 2, …
```

This removes primary clustering but leaves **secondary clustering**: keys with the same home slot still follow the identical sequence. Quadratic probing also may not visit every slot. For squared-attempt offsets modulo an odd prime, the first half-rounded-up set of probes are distinct. If fewer slots are occupied than that number, one of those candidate slots is free. Arbitrary choices of the quadratic coefficients do not share this guarantee.

```formula
R = (m + 1) / 2
R = (7 + 1) / 2 = 4
u < R
where
R: number of distinct first squared-attempt offsets, in slots
m: an odd prime table size, here seven slots
u: number of occupied slots, a nonnegative integer
<: strictly less than
In words: Four first probes have distinct offsets in the seven-slot example; fewer than four occupied slots guarantees a free candidate.
```

A popular variant steps by **triangular numbers** (0, 1, 3, 6, 10, …), which visits every slot when m is a power of two:

```formula
h(k, i) = (h(k) + i (i + 1) / 2) mod m
offsets: 0, 1, 3, 6, 10, 15, 21, 28
mod 8:   0, 1, 3, 6, 2, 7, 5, 4
where
h(k, i): the slot tried on attempt i for key k
h(k): the key's home slot, here 0
k: the key being placed
i: the attempt number, counting from 0
m: the number of slots, a power of two; here 8
mod: "modulo", the remainder after division
offsets: the triangular numbers i × (i + 1) / 2 for i = 0 to 7, each one bigger than the last by i
In words: add 1, then 2, then 3, … to the home slot; in an 8-slot table the first eight tries hit all eight slots exactly once.
```

### Double hashing

Use a second hash to choose the step size:

```formula
h(k, i) = (h_1(k) + i h_2(k)) mod m
h(17, 1) = (3 + 1 × 3) mod 7 = 6
where
h(k, i): the slot tried on attempt i for key k
h_1(k): the first hash, giving the home slot; here h_1(k) = k mod 7, so h_1(17) = 3
h_2(k): the second hash, giving this key's step size; here h_2(k) = 5 − (k mod 5), so h_2(17) = 3
k: the key, here 17
i: the attempt number, counting from 0; here 1, the second try
m: the number of slots, here 7
mod: "modulo", the remainder after division
In words: start at the home slot and move by a key-specific step on each failed attempt; key 17 starts at slot 3 and its second try is slot 6.
```

Keys with the same home slot now usually follow different sequences, reducing clustering when the two hashes distribute keys well; keys sharing both hashes still share a sequence. Two rules: the step h₂(k) must never be 0 (or you probe the same slot forever), and it must be **coprime** with m (share no factor with it other than 1) so the sequence can reach every slot. For prime m, any step that is not a multiple of m works; for power-of-two m, any odd step works.

For the same keys as the linear-probing example, use the second hash defined in the preceding formula: five minus the key’s remainder after division by five.

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
