---
id: cache-short-sets-address-fields
title: Cache sets and address fields
level: intermediate
minutes: 5
sourceLesson: cache-arch-organisation
summary: Divide data capacity by line size and ways to count sets.
---

A cache holds copies of memory lines. The lookup must determine whether the requested bytes are present. The conventional organisations below use address-derived indexing and tag comparison to locate possible entries efficiently. Exact lookup pipelines and latency vary.

## Lines, sets and ways

Three numbers describe a cache:

- Capacity C: total bytes of data (e.g. 32 KiB).
- **Line size** B: bytes per line (e.g. 64).
- **Cache associativity** E: how many places (**cache ways**) a given line may go.

The cache is a grid of equal-sized lines, so dividing the capacity by the line size counts the lines. Those lines are then dealt out into sets of E ways each, so dividing the line count by E counts the sets. You need the set count every time you size an index field or predict which addresses collide:

```formula
N = C / B
S = N / E = C / (BE)
N = 32,768 bytes / (64 bytes) = 512
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

Doubling the ways at the same capacity halves the sets; doubling the capacity at the same ways doubles them. The formula counts bytes of data only: the tags and status bits live in extra storage on top (see the later cache-metadata unit).

A memory line maps to exactly one set, but may sit in any way within that set.

| Organisation | Ways per set | Sets |
|---|---|---|
| Direct-mapped | One | One per cache line |
| Set-associative | Several | Lines divided by ways |
| Fully associative | All lines | One |

## Splitting the address

For this conventional byte-addressed, modulo-indexed model, the address is split into three fields. Mappings that hash or scramble the address need different indexing rules. For the drawing below, the address width is m bits, with t tag bits, s index bits and b offset bits; the next formula card defines how to calculate those widths:

```
 |<-------------- m bits -------------->|
 +------------------+-----------+-------+
 |       tag        |   index   |offset |
 +------------------+-----------+-------+
       t bits          s bits    b bits
```

- Offset: which byte within the line.
- Index: which set to look in.
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

For 64-byte lines and 64 sets, offset and index each need 6 bits, leaving 36 tag bits in a 48-bit address. A base-two logarithm gives a whole-number field width only for a power-of-two count.

The line size and set count must be powers of two for this simple bit-field split. Capacity and way count need not be: 48 KiB with 12 ways and 64-byte lines still has 64 sets.

A lookup then goes:

1. Use the index to select one set.
2. Compare the address's tag against the stored tag of every way in that set, in parallel. A way hits if its tag matches *and* its **valid bit** is set.
3. On a hit, use the offset to pick the bytes out of the line.

## Key takeaways
- Divide data capacity by line size and ways to count sets.
- The conventional power-of-two model divides an address into tag, index and byte offset.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
