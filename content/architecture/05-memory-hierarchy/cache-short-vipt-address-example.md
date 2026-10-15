---
id: cache-short-vipt-address-example
title: Physical tags and VIPT indexing
level: intermediate
minutes: 4
sourceLesson: cache-arch-organisation
summary: Physical address width determines the physical tag.
---

This unit builds on the earlier cache lessons and focuses on physical tags and vipt indexing. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Worked example 2: an L1-style model

Assume 32 KiB, 8 ways, 64-byte lines and 48-bit physical addresses. The tag calculation uses physical addresses; a 48-bit virtual address is not generally its physical tag.

```formula
N = C / B = 32,768 bytes / (64 bytes) = 512
S = N / E = 512 / 8 = 64
b = log_2(64) = 6 bits
s = log_2(64) = 6 bits
t = m − s − b = 48 − 6 − 6 = 36 bits
where
N: the number of lines
C: the capacity, 32 KiB = 32,768 bytes
B: the line size, 64 bytes
E: the ways per set, 8
S: the number of sets
b: the offset width, in bits
s: the index width, in bits
t: the tag width, in bits
m: the physical address width, 48 bits
log_2: logarithm base 2: the power of 2 that gives the number (2^6 = 64)
bytes: the unit of memory size, 8 bits each
bits: binary digits, each 0 or 1
In words: 512 lines in sets of 8 make 64 sets, so offset and index take 6 bits each and the tag takes the other 36.
```

Address `0x7FFE12345678`. The low 12 bits are `0x678` = `0110 0111 1000`. Cut that into a 6-bit index and a 6-bit offset; the tag is the address with those 12 bits removed:

```formula
x_off = 0b111000 = 56
x_idx = 0b011001 = 25
x_tag = ⌊A / 2^12⌋ = 0x7FFE12345
where
x_off: the offset: the low 6 bits
x_idx: the index (set number): the next 6 bits
x_tag: the tag: everything above the low 12 bits
A: the address, 0x7FFE12345678
2^12: 12 copies of 2 multiplied together, 4,096; dividing by it removes the low 12 bits (in code, A >> 12)
⌊ ⌋: floor: round down, dropping the fraction
0b: prefix for a binary number; 0x: prefix for a hexadecimal (base-16) number
In words: this address is byte 56 of a line in set 25, and that line stores the 36-bit tag 0x7FFE12345.
```

> [!tip] Hex shortcut
> When the combined offset and index width is a multiple of 4 bits, read the fields straight off the hex digits. Here the combined width is 12 bits, the last three hexadecimal digits (`678`), so the tag is everything before them: `0x7FFE12345`.

Notice that the combined index and offset width is exactly 12 bits, the size of a 4 KiB page offset. That is not a coincidence. It lets the L1 pick the set using address bits that are the same in the virtual and physical address, so the set lookup can start while the TLB translates the rest (a *virtually indexed, physically tagged* or VIPT cache; translation itself is covered in the OS subject). It is one reason a design might grow L1 by adding ways: 48 KiB with 12 ways also gives 64 sets. Other geometries can use other alias-management techniques.

## Key takeaways
- Physical address width determines the physical tag.
- Indexing within the unchanged page offset enables lookup alongside translation in the stated model.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
