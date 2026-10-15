---
id: cache-short-direct-address-example
title: Decode a direct-mapped address
level: intermediate
minutes: 4
sourceLesson: cache-arch-organisation
summary: Work out the geometry before interpreting an address.
---

This unit builds on the earlier cache lessons and focuses on decode a direct-mapped address. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Worked example 1: a small direct-mapped cache

A 1 KiB direct-mapped cache with 16-byte lines and 32-bit addresses. First calculate the geometry, repeating the earlier definitions so this example stands alone:

```formula
N = C / B = 1,024 bytes / (16 bytes) = 64
S = N / E = 64 / 1 = 64
b = log_2(16) = 4 bits
s = log_2(64) = 6 bits
t = m − s − b = 32 − 6 − 4 = 22 bits
where
N: the number of lines
C: the capacity, 1 KiB = 1,024 bytes
B: the line size, 16 bytes
E: the ways per set: 1, because the cache is direct-mapped
S: the number of sets
b: the offset width, in bits
s: the index width, in bits
t: the tag width, in bits
m: the address width, 32 bits
log_2: logarithm base 2: the power of 2 that gives the number (2^4 = 16, 2^6 = 64)
bytes: the unit of memory size, 8 bits each
bits: binary digits, each 0 or 1
In words: 64 one-line sets need a 6-bit index, 16-byte lines need a 4-bit offset, and the other 22 bits of a 32-bit address are tag.
```

Now break down address `0x00001A2C` by writing it in binary and cutting it into fields from the right:

```
0001 1010 0010 1100
tag    |index |off
000110 100010 1100
```

```formula
x_off = 0b1100 = 12
x_idx = 0b100010 = 34
x_tag = 0b000110 = 6
where
x_off: the offset field's value: the low 4 bits
x_idx: the index field's value: the next 6 bits up
x_tag: the tag field's value: all the bits above those 10
0b: a prefix meaning the digits after it are binary (base 2)
In words: the address names byte 12 of whatever line sits in set 34, and that line must carry tag 6.
```

So byte 12 of the line in set 34, with tag `0x6`. A quicker way, without binary, uses whole-number division. Cutting off the low bits of a number is the same as dividing by a power of two and keeping the whole part:

```formula
x_off = A mod B
x_idx = ⌊A / B⌋ mod S
x_tag = ⌊A / (BS)⌋
A = 0x1A2C = 6,700
x_off = 6,700 mod 16 = 12
x_idx = ⌊6,700 / 16⌋ mod 64
x_idx = 418 mod 64 = 34
x_tag = ⌊6,700 / 1,024⌋ = 6
where
A: the byte address, a number (0x means hexadecimal, base 16: 0x1A2C = 6,700)
B: the line size, 16 bytes
S: the number of sets, 64
x_off: the offset: which byte within the line
x_idx: the index: which set
x_tag: the tag: which of the many lines that share that set
mod: the remainder after whole-number division; 418 mod 64 = 34 because 418 = 6 × 64 + 34
⌊ ⌋: floor: round down to a whole number, dropping any fraction (⌊6,700 / 16⌋ = ⌊418.75⌋ = 418)
In words: the remainder after dividing by the line size is the offset; the line number's remainder after dividing by the set count is the index; what is left above both is the tag.
```

This arithmetic version works for any address and agrees with the bit-cutting version whenever line size and set count are powers of two.

## Key takeaways
- Work out the geometry before interpreting an address.
- Whole-number division and remainders reproduce the tag/index/offset split.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
