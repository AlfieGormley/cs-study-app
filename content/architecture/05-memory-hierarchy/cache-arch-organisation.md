---
id: cache-arch-organisation
title: Cache organisation and address breakdown
level: intermediate
minutes: 14
summary: How a cache decides where a line can live, splitting an address into tag, index and offset, direct-mapped vs set-associative vs fully associative, the three Cs of misses, and replacement policies.
---

A cache holds copies of memory lines. The lookup must determine whether the requested bytes are present. The conventional organisations below use address-derived indexing and tag comparison to locate possible entries efficiently. Exact lookup pipelines and latency vary.

## Lines, sets and ways

Three numbers describe a cache:

- **Capacity** C: total bytes of data (e.g. 32 KiB).
- **Line size** B: bytes per line (e.g. 64).
- **Cache associativity** E: how many places (**cache ways**) a given line may go.

The cache is a grid of equal-sized lines, so dividing the capacity by the line size counts the lines. Those lines are then dealt out into **sets** of E ways each, so dividing the line count by E counts the sets. You need the set count every time you size an index field or predict which addresses collide:

```formula
N = C / B
S = N / E = C / (B × E)
N = 32,768 bytes / 64 bytes = 512
S = 512 / 8 = 64
where
N: the number of lines the cache can hold (a plain count, no unit)
C: the capacity: total bytes of data, not counting tags; here 32 KiB = 32,768 bytes
B: the line size, here 64 bytes
E: the associativity: the number of ways (slots) in each set, here 8
S: the number of sets (a plain count)
bytes: the unit of memory size; one byte is 8 bits
In words: a 32 KiB cache of 64-byte lines holds 512 lines; grouped 8 to a set, that is 64 sets.
```

Doubling the ways at the same capacity halves the sets; doubling the capacity at the same ways doubles them. The formula counts bytes of data only: the tags and status bits live in extra storage on top (see "Storage overhead" below).

A memory line maps to exactly **one set**, but may sit in **any way** within that set.

| Organisation | Ways per set | Sets |
|---|---|---|
| Direct-mapped | 1 | C / B |
| E-way set-associative | E | C / (B × E) |
| Fully associative | all lines | 1 |

## Splitting the address

For this conventional byte-addressed, modulo-indexed model, the address is split into three fields. Mappings that hash or skew the address need different indexing rules. For an address of *m* bits:

```
 |<-------------- m bits -------------->|
 +------------------+-----------+-------+
 |       tag        |   index   |offset |
 +------------------+-----------+-------+
       t bits          s bits    b bits
```

- **Offset**: which byte within the line.
- **Index**: which set to look in.
- **Cache tag** (tag): the remaining high bits, stored alongside each line and compared to tell apart the many memory lines that share a set.

How wide is each field? Each extra bit doubles the number of values a field can hold (1 bit gives 2 values, 2 bits give 4, 6 bits give 64), so the offset needs just enough bits to number every byte of a line, and the index just enough to number every set. "Just enough bits" is what log base 2 gives you:

```formula
b = log_2(B)
s = log_2(S)
t = m − s − b
where
b: the width of the offset field, in bits
B: the line size, in bytes
s: the width of the index field, in bits
S: the number of sets
t: the width of the tag field, in bits: whatever is left
m: the width of the whole address, in bits (for example 32 or 48)
log_2: logarithm base 2: the power you must raise 2 to in order to get the number; log_2(64) = 6 because 2 × 2 × 2 × 2 × 2 × 2 = 64
In words: the offset gets enough bits to count the bytes in a line, the index gets enough bits to count the sets, and the tag gets every remaining address bit.
```

For 64-byte lines and 64 sets that is 6 offset bits and 6 index bits, leaving 48 − 12 = 36 tag bits for a 48-bit address. log_2 only gives a whole number of bits when its input is a power of two, which is why the split needs one.

The line size and set count must be powers of two for this simple bit-field split. Capacity and way count need not be: 48 KiB with 12 ways and 64-byte lines still has 64 sets.

A lookup then goes:

1. Use the **index** to select one set.
2. Compare the address's **tag** against the stored tag of every way in that set, in parallel. A way hits if its tag matches *and* its **valid bit** is set.
3. On a hit, use the **offset** to pick the bytes out of the line.

### Worked example 1: a small direct-mapped cache

A 1 KiB direct-mapped cache with 16-byte lines and 32-bit addresses. First the geometry, using the two formulas above:

```formula
N = C / B = 1,024 bytes / 16 bytes = 64
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
x_tag = ⌊A / (B × S)⌋
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

### Worked example 2: an L1-style model

Assume 32 KiB, 8 ways, 64-byte lines and 48-bit physical addresses. The tag calculation uses physical addresses; a 48-bit virtual address is not generally its physical tag.

```formula
N = C / B = 32,768 bytes / 64 bytes = 512
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
> When offset + index is a multiple of 4 bits, read the fields straight off the hex digits. Here offset + index = 12 bits = the last three hex digits (`678`), so the tag is everything before them: `0x7FFE12345`.

Notice that index + offset is exactly 12 bits, the size of a 4 KiB page offset. That is not a coincidence. It lets the L1 pick the set using address bits that are the same in the virtual and physical address, so the set lookup can start while the TLB translates the rest (a *virtually indexed, physically tagged* or VIPT cache; translation itself is covered in the OS subject). It is one reason a design might grow L1 by adding ways: 48 KiB with 12 ways also gives 64 sets. Other geometries can use other alias-management techniques.

## Direct-mapped: simple but fragile

Each line has exactly one home. Lookup is fast (one tag compare) and cheap in hardware. The weakness is **conflict**: two hot lines whose addresses share an index keep evicting each other, even if the rest of the cache is empty.

Take a tiny 128-byte cache with 16-byte lines (8 lines) and this trace, with an initially empty cache, demand-only reads and no interference:

```
 0x00 0x04 0x80 0x00 0x84 0x10 0x90 0x10
```

Direct-mapped, 8 sets: offset 4 bits, index 3 bits. `0x00` and `0x80` both have index 0 (tags 0 and 1); `0x10` and `0x90` both have index 1.

| Addr | Set | Tag | Result |
|---|---|---|---|
| 0x00 | 0 | 0 | miss |
| 0x04 | 0 | 0 | hit |
| 0x80 | 0 | 1 | miss (evicts 0) |
| 0x00 | 0 | 0 | miss (evicts 1) |
| 0x84 | 0 | 1 | miss |
| 0x10 | 1 | 0 | miss |
| 0x90 | 1 | 1 | miss |
| 0x10 | 1 | 0 | miss |

**1 hit in 8**, with six of the eight lines sitting empty the whole time.

## Set-associative: the usual compromise

Make the same 128 bytes **2-way**: 4 sets of 2 ways. Now the index is 2 bits; the tag occupies address-width minus 6 bits (2 tag bits if addresses are 8 bits). `0x00` (tag 0) and `0x80` (tag 2) both go to set 0, but there are two ways, so they coexist. With LRU replacement:

| Addr | Set | Tag | Result |
|---|---|---|---|
| 0x00 | 0 | 0 | miss |
| 0x04 | 0 | 0 | hit |
| 0x80 | 0 | 2 | miss |
| 0x00 | 0 | 0 | hit |
| 0x84 | 0 | 2 | hit |
| 0x10 | 1 | 0 | miss |
| 0x90 | 1 | 2 | miss |
| 0x10 | 1 | 0 | hit |

**4 hits in 8.** The remaining misses are all first-time (compulsory) misses. Making it fully associative would not help this trace any further.

The price of associativity is hardware: one tag comparator per way, all working in parallel, a multiplexer to choose the hitting way, and replacement state. More ways usually means slightly higher hit time and power. Exact associativities depend on the named cache.

> A generic L1/L2/L3 associativity table is omitted because the earlier ranges were not verified against a representative set of specified processors.

## The three Cs of misses

Classifying misses tells you what would fix them:

- **Compulsory miss** (cold miss): the first access to a line. Prefetching can turn a first demand access into a hit; changing line size or avoiding accesses also changes the count.
- **Capacity miss**: the working set is bigger than the cache. In the conventional three-C classification, a previously seen line also misses in a fully associative LRU reference cache of the same capacity and line size. Fix with a bigger cache or better locality (loop blocking).
- **Conflict miss**: a previously seen line misses here but hits in that fully associative reference cache, often because competing lines share a set. Fix with more associativity, or by changing addresses (padding).

Multicore systems add a fourth C, **coherence** misses, when another core invalidated your copy (see the coherence lesson).

## Replacement: choosing a victim

In a set-associative cache, allocating a new line into a full set requires a victim; a bypassed or no-write-allocate access need not allocate.

- **LRU**: evict the least recently used way. Exact LRU for 8 ways needs to track an ordering of 8 items per set, which is costly.
- **Pseudo-LRU (tree-PLRU)**: for a power-of-two number of ways, a binary tree with one bit fewer than the number of ways in each set (7 bits for 8 ways) points roughly away from recent accesses. It uses less state than a full ordering, but can choose a different victim from true LRU.
- **RRIP-style policies**: give each line a small "re-reference prediction" counter so that lines that were used only once (a streaming scan) are evicted before reused lines. Such policies can resist scans; a particular processor’s policy requires implementation documentation.
- **Random replacement** (pseudo-random): choose a victim using a random or pseudo-random mechanism. This can avoid maintaining a recency order; effectiveness is trace-dependent.

## Storage overhead

The data array is not the whole cache. Each line also stores its tag, a valid bit and (for a write-back cache) a dirty bit, plus replacement bits per set. To size that metadata, add up the bits one line needs and multiply by the number of lines. For the 32 KiB 8-way example from worked example 2:

```formula
M_line = t + 1 + 1
M_line = 36 + 1 + 1 = 38 bits
M_all = N × M_line = 512 × 38 bits
M_all = 19,456 bits = 2,432 bytes
f = 2,432 bytes / 32,768 bytes ≈ 7.4 %
where
M_line: metadata bits stored for one line
t: the tag width, 36 bits in this example
1: one bit each for the valid bit and the dirty bit
N: the number of lines, 512
M_all: metadata for the whole cache, in bits and then bytes (8 bits per byte)
f: the metadata as a fraction of the data capacity
bits: binary digits, each 0 or 1
bytes: the unit of memory size, 8 bits each
≈: approximately equal to (rounded)
%: per cent, parts per hundred
In words: 38 extra bits on each of 512 lines comes to about 2.4 KB, roughly 7.4 % on top of the 32 KiB of data.
```

That figure is a floor: replacement state, coherence state and error-checking bits add more, and a larger address or smaller cache means a wider tag and so a larger fraction.

## Pitfalls

- **Power-of-two strides.** In the 64-set, 64-byte-line model, 64 sets × 64 bytes = 4,096 bytes, so strides divisible by 4,096 bytes retain the same set index. An 8-way set holds only eight such lines. Padding can spread rows across sets, but whether it prevents thrashing depends on the new stride and working set. (The friendly-code lesson works through this.)
- **Forgetting the tag bits shrink as the cache grows.** Doubling the number of sets moves one bit from tag to index.
- **Mixing up KB and KiB.** KiB denotes a binary unit: 32 KiB = 32,768 bytes; KB denotes 1,000 bytes when used in the SI sense.

## Key takeaways
- The number of sets is the capacity divided by (line size × ways). The offset needs enough bits to number the bytes in a line, the index enough to number the sets, and the tag takes the rest.
- Lookup: the index picks a set, all its tags are compared in parallel, the offset selects the bytes.
- Direct-mapped is fast but suffers conflict misses; set-associative is the standard compromise; fully associative placement removes set restrictions but can be costly to implement at large capacity.
- Misses are compulsory, capacity, conflict (and, on multicore, coherence); each has a different cure.
- Replacement may use tree-PLRU, RRIP-style, random or other policies; do not infer a processor’s exact policy from associativity alone.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
