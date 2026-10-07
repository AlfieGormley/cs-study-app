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

- **Capacity** C: total data bytes (e.g. 32 KiB).
- **Line size** B: bytes per line (e.g. 64).
- **Associativity** E: how many places (**ways**) a given line may go.

From these, the number of lines is C / B, and the lines are grouped into **sets** of E ways each:

```
 sets S = C / (B x E)
```

A memory line maps to exactly **one set**, but may sit in **any way** within that set.

| Organisation | Ways per set | Sets |
|---|---|---|
| Direct-mapped | 1 | C / B |
| E-way set-associative | E | C / (B·E) |
| Fully associative | all lines | 1 |

## Splitting the address

For this conventional byte-addressed, modulo-indexed model, the address is split into three fields. Hashed and skewed mappings need different indexing rules. For an address of *m* bits:

```
 |<-------------- m bits -------------->|
 +------------------+-----------+-------+
 |       tag        |   index   |offset |
 +------------------+-----------+-------+
   t = m - s - b       s bits    b bits
```

- **Offset** (b bits, b = log2 B): which byte within the line.
- **Index** (s bits, s = log2 S): which set to look in.
- **Tag** (the remaining t = m − s − b bits): stored alongside each line, and compared to tell apart the many memory lines that share a set.

The line size B and set count S must be powers of two for this simple bit-field split. Capacity C and way count E need not be: 48 KiB with 12 ways and 64-byte lines still has 64 sets.

A lookup then goes:

1. Use the **index** to select one set.
2. Compare the address's **tag** against the stored tag of every way in that set, in parallel. A way hits if its tag matches *and* its **valid bit** is set.
3. On a hit, use the **offset** to pick the bytes out of the line.

### Worked example 1: a small direct-mapped cache

A 1 KiB direct-mapped cache with 16-byte lines and 32-bit addresses.

1. Lines = 1024 / 16 = 64. Direct-mapped, so sets = 64.
2. Offset b = log2 16 = **4** bits.
3. Index s = log2 64 = **6** bits.
4. Tag t = 32 − 6 − 4 = **22** bits.

Now break down address `0x00001A2C`:

```
 0x1A2C = 0001 1010 0010 1100
 offset = low 4 bits    = 1100   = 12
 index  = next 6 bits   = 100010 = 34
 tag    = remaining     = 000110 = 6
```

So byte 12 of the line in set 34, with tag `0x6`. A quicker way: offset = addr mod 16 = 12; index = (addr div 16) mod 64 = 418 mod 64 = 34; tag = addr div 1024 = 6.

### Worked example 2: an L1-style model

Assume 32 KiB, 8 ways, 64-byte lines and 48-bit physical addresses. The tag calculation uses physical addresses; a 48-bit virtual address is not generally its physical tag.

1. Lines = 32,768 / 64 = 512.
2. Sets = 512 / 8 = **64**.
3. Offset = log2 64 = **6** bits; index = log2 64 = **6** bits.
4. Tag = 48 − 6 − 6 = **36** bits.

Address `0x7FFE12345678`. The low 12 bits are `0x678` = `0110 0111 1000`:

```
 offset = 111000   = 56
 index  = 011001   = 25
 tag    = addr >> 12 = 0x7FFE12345
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

The price of associativity is hardware: E tag comparators working in parallel, a multiplexer to choose the hitting way, and replacement state. More ways usually means slightly higher hit time and power. Exact associativities depend on the named cache.

> A generic L1/L2/L3 associativity table is omitted because the earlier ranges were not verified against a representative set of specified processors.

## The three Cs of misses

Classifying misses tells you what would fix them:

- **Compulsory** (cold): the first access to a line. Prefetching can turn a first demand access into a hit; changing line size or avoiding accesses also changes the count.
- **Capacity**: the working set is bigger than the cache. In the conventional three-C classification, a previously seen line also misses in a fully associative LRU reference cache of the same capacity and line size. Fix with a bigger cache or better locality (blocking).
- **Conflict**: a previously seen line misses here but hits in that fully associative reference cache, often because competing lines share a set. Fix with more associativity, or by changing addresses (padding).

Multicore systems add a fourth C, **coherence** misses, when another core invalidated your copy (see the coherence lesson).

## Replacement: choosing a victim

In a set-associative cache, allocating a new line into a full set requires a victim; a bypassed or no-write-allocate access need not allocate.

- **LRU**: evict the least recently used way. Exact LRU for 8 ways needs to track an ordering of 8 items per set, which is costly.
- **Pseudo-LRU (tree-PLRU)**: for a power-of-two E, a binary tree of E − 1 bits per set (7 bits for 8 ways) points roughly away from recent accesses. It uses less state than a full ordering, but can choose a different victim from true LRU.
- **RRIP-style policies**: give each line a small "re-reference prediction" counter so that lines that were used only once (a streaming scan) are evicted before reused lines. Such policies can resist scans; a particular processor’s policy requires implementation documentation.
- **Random** (pseudo-random): choose a victim using a random or pseudo-random mechanism. This can avoid maintaining a recency order; effectiveness is trace-dependent.

## Storage overhead

The data array is not the whole cache. Each line also stores its tag, a valid bit and (for a write-back cache) a dirty bit, plus replacement bits per set. For the 32 KiB 8-way example: 36 tag + 1 valid + 1 dirty = 38 bits per line, × 512 lines = 19,456 bits = 2,432 bytes, about 7.4% on top of the 32 KiB of data (before replacement and coherence state).

## Pitfalls

- **Power-of-two strides.** In the 64-set,64-byte-line model, strides divisible by 4,096 bytes retain the same set index. An 8-way set holds only eight such lines. Padding can spread rows across sets, but whether it prevents thrashing depends on the new stride and working set. (The friendly-code lesson works through this.)
- **Forgetting the tag bits shrink as the cache grows.** Doubling the number of sets moves one bit from tag to index.
- **Mixing up KB and KiB.** KiB denotes a binary unit: 32 KiB = 32,768 bytes; KB denotes 1,000 bytes when used in the SI sense.

## Key takeaways
- sets = capacity / (line size × ways); offset = log2(line size), index = log2(sets), tag = the rest.
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
