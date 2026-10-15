---
id: cache-short-working-access-order
title: Working sets and access order
level: basic
minutes: 5
sourceLesson: cache-arch-locality
summary: A fitting working set enables reuse without guaranteeing hits.
---

This unit builds on the earlier cache lessons and focuses on working sets and access order. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Hits, misses and the working set

Some vocabulary used throughout this module:

- **Cache hit** (hit): the data is in this level. **Cache miss** (miss): it is not, and the request goes to the next level down.
- **Hit rate** and **miss rate**: the fractions of accesses that hit and miss (formulas below).
- **Miss penalty**: the extra time a miss costs (the time to get the line from below).
- **Working set**: the data a program touches over a short window of time. Fitting in a level makes reuse possible, but set conflicts, other activity, coherence and replacement policy can still evict data. Exceeding capacity can increase misses.

Every access either hits or misses, so the two rates always add up to 1:

```formula
h = N_hits / N_acc
m = 1 − h
where
h: the hit rate, a fraction from 0 to 1 (often written as a percentage)
m: the miss rate, a fraction from 0 to 1
N_hits: the number of accesses that hit in this level
N_acc: the total number of accesses to this level
In words: the hit rate is the share of accesses that found their data here, and the miss rate is everything else.
```

For example, 950 hits out of 1,000 accesses is a hit rate of 0.95 (95 %) and a miss rate of 0.05 (5 %). These are rates for one level: an L2 miss rate here counts only the accesses that reached L2 (the AMAT lesson calls this the local miss rate, and also defines a global one).

The working set is why performance graphs often show **performance cliffs**. A carefully controlled repeated-access benchmark may show transitions near cache capacities. Streaming bandwidth, prefetching and access dependencies can make the curve quite different. The staircase below is schematic: its size labels are hypothetical boundaries, not measurements or a processor specification.

```
time per
access
  ^                          ______ DRAM
  |                  _______/
  |          _______/  L3
  |  _______/ L2
  |__/ L1
  +--------------------------> size
    32K    1M         32M
```

## Seeing locality in code

The same amount of work can have very different locality. Both functions below add up the same list of numbers; only the order differs.

```python
import random

N = 10_000_000
# Slots hold references to int objects.
data = list(range(N))

def in_order():
    total = 0
    # Neighbouring reference slots are read.
    for i in range(N):
        total += data[i]
    return total

order = list(range(N))
random.shuffle(order)
# Shuffled indices scatter reference reads.

def shuffled():
    total = 0
    # Same values; a different access order.
    for i in order:
        total += data[i]
    return total
```

In CPython, a list contains references to objects. Sequentially reading the reference array has spatial locality; shuffled indices scatter those accesses and can increase cache misses. Object allocation, shared objects, interpreter work, the extra array of indices and cache size affect the result. Run a controlled benchmark rather than assuming a fixed slowdown.

> A universal 5–10× slowdown and interpreter nanoseconds-per-iteration figure are omitted because no matching runtime, machine and benchmark were verified.

## Real-world consequences

- Arrays can improve traversal locality compared with scattered linked lists, even at the same big-O complexity. A dependent `next` pointer limits when the next demand address becomes known; whether it misses depends on placement, residency and prefetch capabilities.
- B-trees can reduce serial node accesses compared with binary trees for large indexes. A B-tree node is sized to hold many keys in a few cache lines (or one disk page), so each visited node can provide several nearby keys. A node may span several lines; cache misses depend on residency and search layout.
- Hot loops should be small. Instructions are cached too (in a separate L1 instruction cache). Huge unrolled or inlined code can overflow it.
- Data size matters. Using `int32` instead of `int64` fits twice as many integers per line; packing one-byte booleans into bits fits eight times as many flags, excluding layout overhead.

## Pitfalls

- Assuming the big-O tells the whole story. Two O(n) algorithms (time growing in proportion to n, the number of elements) can differ by 10× because one streams memory and the other jumps around.
- Benchmarking with tiny inputs. If the test data fits in L1, you are measuring the fast path. Production data that overflows into DRAM behaves differently.
- Assuming 64-byte lines everywhere. Line sizes vary by processor and cache level. Query the target (`sysctl hw.cachelinesize` on macOS, `getconf LEVEL1_DCACHE_LINESIZE` on Linux) rather than hard-coding it in portable code.

## Key takeaways
- A fitting working set enables reuse without guaranteeing hits.
- Sequential reference-array access and dependent pointer chains have different locality and overlap opportunities.

## Further reading
- [CMU: Memory hierarchy](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/11-memory-hierarchy.pdf)
- [Intel Memory Latency Checker](https://www.intel.com/content/www/us/en/developer/articles/tool/intelr-memory-latency-checker.html)
- [Memory hierarchy — Wikipedia](https://en.wikipedia.org/wiki/Memory_hierarchy)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [What every programmer should know about memory, Ulrich Drepper (LWN)](https://lwn.net/Articles/250967/)
- [Gallery of processor cache effects, Igor Ostrovsky](https://igoro.com/archive/gallery-of-processor-cache-effects/)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
