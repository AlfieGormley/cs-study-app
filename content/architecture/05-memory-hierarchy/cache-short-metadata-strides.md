---
id: cache-short-metadata-strides
title: Cache metadata and indexing pitfalls
level: intermediate
minutes: 3
sourceLesson: cache-arch-organisation
summary: Tags and status bits add storage beyond the advertised data capacity.
---

This unit builds on the earlier cache lessons and focuses on cache metadata and indexing pitfalls. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Storage overhead

The data array is not the whole cache. Each line also stores its tag, a valid bit and (for a write-back cache) a dirty bit, plus replacement bits per set. To size that metadata, add up the bits one line needs and multiply by the number of lines. For the 32 KiB 8-way example from worked example 2:

```formula
M_line = t + 1 + 1
M_line = 36 + 1 + 1 = 38 bits
M_all = N M_line = 512 × 38 bits
M_all = 19,456 bits = 2,432 bytes
f = 2,432 bytes / (32,768 bytes) ≈ 7.4 %
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

That figure is a floor: replacement state, coherence state and error-checking bits add more, and a wider physical address increases tag width; fewer sets also widen the tag when the remaining geometry is held fixed.

## Pitfalls

- Power-of-two strides. In the 64-set, 64-byte-line model, 64 sets × 64 bytes = 4,096 bytes, so strides divisible by 4,096 bytes retain the same set index. An 8-way set holds only eight such lines. Padding can spread rows across sets, but whether it prevents thrashing depends on the new stride and working set. (The friendly-code lesson works through this.)
- Forgetting the tag bits shrink as the cache grows. Doubling the number of sets moves one bit from tag to index.
- Mixing up KB and KiB. KiB denotes a binary unit: 32 KiB = 32,768 bytes; KB denotes 1,000 bytes when used in the SI sense.

## Key takeaways
- Tags and status bits add storage beyond the advertised data capacity.
- Simple modulo indexing can make a power-of-two stride repeatedly select one set.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
