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

```formula essential
T = O(d(n + b))
where
T: the running time of LSD radix sort
O: Big O: grows at most this fast, up to a constant factor
d: the number of digits per key, which is the number of passes
n: the number of keys
b: the base: how many values one digit can take, which is the size of each pass's counter table
In words: radix sort does one pass per digit, and each pass touches every key once plus a table of b counters.
```

The cost depends on the **key width** (through d) rather than on comparisons. A comparison sort's cost instead grows with n log n, whatever the keys look like. So radix sort tends to win when keys are short and fixed-width and n is large, and tends to lose when keys are long (many digits) or n is small; measure for your own data.

For 32-bit unsigned integers with base 256 (one byte per digit): four passes cover the full key width. A 256-entry table of four-byte counters needs 1 KiB and fits in many L1 data caches; Python counter objects have different storage overhead. For 10 million keys, that is 40 million output placements across the digit passes, plus counting reads and other overhead, versus roughly 230 million comparisons for an n log n comparison sort. Those are different operations, so the counts alone do not give a speed ratio.

> [!warning] Radix sort depends on key width
> The bound above assumes each digit operation costs a constant amount. It is "linear" only because the number of digits is treated as fixed. Python arbitrary-size integer division has its own bit cost.

How many digits are there? Divide the key width by the bits in one digit: 32-bit keys in base 256 (8 bits per digit) take 4 passes, and 64-bit keys take 8. That depends on the key width, not on n, but n distinct keys need at least enough digits to tell them apart: 10 million distinct keys cannot fit in fewer than 3 bytes.

```formula reference
d = ⌈w / log_2(b)⌉
d ≥ ⌈log_b(n)⌉
where
d: the number of digits (passes)
w: the key width in bits
b: the base, the number of values one digit can take
log_2(b): the number of bits in one digit; log_2(256) = 8
log_b(n): the logarithm of n to base b: the power you raise b to in order to get n
n: the number of keys, all distinct
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
In words: the number of passes is the key width divided by the bits per digit, rounded up, and distinct keys need at least enough digits to tell them all apart.
```

That lower bound on d does not imply an upper bound: keys can be much wider. Fixed 32- or 64-bit keys give a fixed number of passes, with at most 2³² or 2⁶⁴ distinct values.

Choosing the base is a trade-off. Base 2¹⁶ means 2 passes for 32-bit keys, but clearing 65,536 counters costs more and the table may exceed the target CPU cache. Base 2⁸ uses a smaller table. The best base depends on counter representation, hardware and workload.

## Key takeaways
- Pass count depends on key width and digit base.
- Large counter tables and arbitrary-precision digit operations change practical cost.

## Further reading
- [LSD and MSD radix sorting — Princeton Algorithms](https://algs4.cs.princeton.edu/51radix/)
