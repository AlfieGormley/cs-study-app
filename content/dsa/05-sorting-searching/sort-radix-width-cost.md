---
id: sort-radix-width-cost
title: Radix width, base and pass costs
level: intermediate
minutes: 4
sourceLesson: sort-linear-time
summary: Pass count depends on key width and digit base.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### What radix sort really costs

Each pass is a counting sort over one digit, so it costs O(n + b) for a digit with b possible values. Multiply by the number of passes:

```formula
T = O(d(n + b))
P = dn = 4 × 10^7
C = n log_2(n) ≈ 10^7 × 23.3 ≈ 2.3 × 10^8
where
T: the running time of LSD radix sort
O: Big O: grows at most this fast, up to a constant factor
d: the number of digits per key, which is the number of passes; 4 here (32-bit keys, one byte per digit)
n: the number of keys; 10 million (10^7) here
b: the base: how many values one digit can take; 256 here, one byte
P: the total output placements across all the passes
C: roughly the comparisons an n log n comparison sort would make on the same keys
log_2(n): the base-2 logarithm of n; log_2(10^7) ≈ 23.3
10^7: ten to the power 7, ten million
≈: approximately equal to
In words: radix sort does d passes, each touching every key once plus a table of b counters; for 32-bit keys in base 256 that is 4 passes.
```

For 32-bit unsigned integers with base 256 (one byte per digit): four passes cover the full key width. A 256-entry table of four-byte counters needs 1 KiB and fits in many L1 data caches; Python counter objects have different storage overhead. For 10 million keys, that is 40 million output placements across the digit passes, plus counting reads and other overhead, versus roughly 230 million comparisons for an linear times logarithmic growth sort.

> [!warning] Radix sort depends on key width
> The bound above assumes each digit operation costs a constant amount. It is "linear" only because the number of digits is treated as fixed. Python arbitrary-size integer division has its own bit cost.

How many digits are there? It depends on the key width, not on n, but n distinct keys need at least enough digits to tell them apart:

```formula
d = ⌈w / log_2(b)⌉
d = 32 / log_2(256) = 32 / 8 = 4
d ≥ ⌈log_b(n)⌉
where
d: the number of digits (passes)
w: the key width in bits; 32 here
b: the base, the number of values one digit can take; 256 here
log_2(b): the number of bits in one digit; log_2(256) = 8
log_b(n): the logarithm of n to base b: the power you raise b to in order to get n
n: the number of keys, all distinct
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
In words: 32-bit keys in base 256 always take 4 passes, and n distinct keys can never fit in fewer than log_b(n) digits.
```

That lower bound on d does not imply an upper bound: keys can be much wider. Fixed 32- or 64-bit keys give a fixed number of passes, with at most 2³² or 2⁶⁴ distinct values.
Choosing the base is a trade-off. Base 2¹⁶ means 2 passes for 32-bit keys, but clearing 65,536 counters costs more and the table may exceed the target CPU cache. Base 2⁸ uses a smaller table. The best base depends on counter representation, hardware and workload.

## Key takeaways
- Pass count depends on key width and digit base.
- Large counter tables and arbitrary-precision digit operations change practical cost.

## Further reading
- [LSD and MSD radix sorting — Princeton Algorithms](https://algs4.cs.princeton.edu/51radix/)
