---
id: sort-radix-encoded-keys
title: Radix sorting strings and signed keys
level: intermediate
minutes: 2
sourceLesson: sort-linear-time
summary: MSD sorting follows distinguishing prefixes and can stop early.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### MSD radix sort and strings

**MSD (most significant digit)** radix sort starts from the first digit, splits into buckets, and recurses into each bucket. It suits variable-length strings: you can stop as soon as a bucket has one element, and you never look at characters beyond the distinguishing prefix. Stability depends on the MSD implementation; in-place variants may be unstable. Many implementations switch to insertion sort for small buckets. Sorting strings this way is the basis of suffix array construction and some fast string-sorting libraries.

### Negative numbers and floats

- **Signed integers:** flip the sign bit before sorting (XOR with `0x80000000` for 32-bit), so negatives come first.
- **IEEE-754 floats:** positive floats already sort correctly as unsigned integers. For negatives, flip all the bits; for positives, flip just the sign bit. For non-NaN IEEE binary values this maps numerical order to unsigned-key order. Specify NaN placement and whether -0.0 and +0.0 must be treated as equivalent; simple bit transforms alone do not establish that policy.

## Key takeaways
- MSD sorting follows distinguishing prefixes and can stop early.
- Signed and floating keys require an order-preserving encoding and an explicit NaN policy.

## Further reading
- [LSD and MSD radix sorting — Princeton Algorithms](https://algs4.cs.princeton.edu/51radix/)
- [NVIDIA radix transforms and floating-point policies](https://github.com/NVIDIA/cccl/blob/main/cub/cub/device/device_radix_sort.cuh)
