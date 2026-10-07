---
id: hash-resizing
title: Load factor and resizing
level: intermediate
minutes: 12
summary: Why tables grow at a fixed load factor, why doubling makes inserts amortised O(1), and how CPython's dict and Java's HashMap (with its Java 8 tree bins) actually work.
---

A hash table's speed depends on one ratio: how full it is. The **load factor** is

```
alpha = n / m
  n = keys stored
  m = buckets (slots)
```

Keep α low and buckets are mostly empty or hold a single key, so operations are fast. Let α creep up and chains lengthen or probe runs grow. Many dynamically growing tables therefore watch α and, when it passes a **maximum load factor**, allocates a bigger array and moves everything across. This lesson is about that move: what it costs, why it is still cheap on average, and how two widely used implementations do it.

## Choosing the maximum load factor

The threshold is a space–time trade-off. A low maximum wastes memory on empty slots; a high one makes operations slower.

| Table | Typical/default growth policy | Scheme |
|---|---|---|
| Java `HashMap` | 0.75 | chaining |
| CPython `dict` | about 2/3 | open addressing |
| Abseil Swiss table | 7/8 | open addressing + SIMD |
| Redis dict | normally grows near 1; policy can defer growth | chaining |

Chaining tolerates higher α because a slightly longer chain is a mild slowdown. Classical linear-probing miss estimates grow like 1/(1 − α)² under their random-hashing assumptions. This is not the formula for every probing design. Metadata group comparisons help Swiss-table implementations at higher load.

## Rehashing: why every key moves

When the table grows from m to m′ buckets, you cannot copy the old array across as it is. A key's bucket is `hash mod m`, so changing m can change a key's bucket (doubling moves about half under uniform hashing). Growing therefore means **rehashing**: walking every entry and inserting it into the new array.

```
old m = 4         new m = 8
hash  idx         hash  idx
  5    1            5    5
  9    1            9    1
 14    2           14    6
```

Visiting/copying entries costs O(n); placing them by ordinary probing assumes well-distributed hashes for expected O(n), and collision-heavy reinsertion can cost more. Implementations usually store each entry's full hash so they do not have to recompute it (which matters for long strings), but every entry still has to be visited and placed.

## Amortised analysis: why inserts are still O(1)

One O(n) insert sounds bad. The trick is that, if the table grows by a constant **factor**, expensive inserts become rarer as the table grows.

Count the copying work for n inserts into a table that starts with one slot and doubles when full. First assume n is a power of two:

```
resize at size: 1, 2, 4, ..., n/2
copies: 1 + 2 + 4 + ... + n/2  <  n
```

For powers of two this is fewer than n copies. For arbitrary n, the last copied capacity can exceed n/2, but the total is still fewer than 2n copies, or fewer than 3n units including placements. Thus **resizing overhead** is amortised O(1) per insert for every sequence. Overall hash-table insertion also depends on collision costs: the usual bound is expected amortised O(1), assuming well-distributed hashes and constant-time key operations.

Growing by a constant **amount** does not work. Add 10 slots each time and you copy 10 + 20 + 30 + … keys, about n²/20 in total: O(n) per insert.

```python
def total_copies(n, grow):
    cap, size, copies = 1, 0, 0
    for _ in range(n):
        if size == cap:
            copies += size
            cap = grow(cap)
        size += 1
    return copies

total_copies(1000, lambda c: 2 * c)
# 1023
total_copies(1000, lambda c: c + 10)
# 49600
```

> [!note] The banker's view
> Charge each insert 3 units instead of 1. One pays for the insert itself; two are saved. By the time a table of size m fills and doubles, the m/2 inserts since the last resize have saved m units, exactly enough to pay for moving all m keys. No operation ever runs up a debt, so the average stays at 3.

### Shrinking without thrashing

If a table also shrinks when it empties, do not use the same threshold in both directions. Grow at α = 1 and shrink at α = ½, and a workload hovering at the boundary (insert, delete, insert, …) would resize on every operation. The textbook fix is a gap: double when full, halve when α falls to ¼. Many real tables simply never shrink automatically; CPython's dict does not shrink when you delete keys.

### When amortised is not good enough

Amortised O(1) still means an occasional O(n) pause. The pause depends on the implementation, key count, allocator and hardware; measure it against the server's latency budget.

**Incremental rehashing** spreads the work out. Redis keeps two tables during a resize and moves a few buckets on each operation (plus a little work in a background timer). Lookups check both tables until the move completes. Go's built-in map used a similar gradual "evacuation" before its Go 1.24 redesign. The cost is complexity and, temporarily retaining both bucket arrays (m + 2m buckets when doubling, excluding entries and other overhead).

If you know the final size, the simplest fix is to **pre-size** the table to avoid growth for the planned live-key count. Deletion churn can still require compaction/rebuilds.

## How CPython's dict works

CPython's dict is open addressing with a **compact** layout, introduced in Python 3.6 and based on a 2012 proposal by Raymond Hettinger. The simplified description below covers an ordinary combined table with general keys. Split/key-sharing tables and Unicode-only entries have different layouts. There are two arrays:

```
indices (small ints, 1 per slot)
[ -,  1,  -,  0,  -,  -,  2,  - ]

entries (dense, insertion order)
0: hash, 'cat', 1
1: hash, 'dog', 2
2: hash, 'eel', 3
```

- The **indices** array is the hash table proper. Each slot holds an index into `entries`, and uses 1, 2, 4 or 8 bytes depending on the table size, so a small dict's index is tiny.
- The **entries** array stores (hash, key, value) in insertion order. That is why dicts preserve insertion order: iteration just walks `entries`.

Compared with the old design, which stored full 24-byte entries in a sparse array, this saves a lot of memory, because only the cheap index array is sparse.

Further details:

- **Sizes** are powers of two, minimum 8. A table of size m holds at most ⅔m entries (5 in a table of 8).
- **Growth**: when full, the new size is the smallest power of two that is at least 3 × the number of live keys. Without deletions this doubles the table: in CPython 3.14, a dict built key by key resizes on the 6th, 11th, 22nd and 43rd inserts.
- **Probing** uses a perturbed sequence, not linear steps. Starting from `i = hash & mask`, each step is `perturb >>= 5` then `i = (5*i + perturb + 1) & mask`. The shifting `perturb` feeds the high bits of the hash into the sequence, so keys that share low bits soon diverge; once `perturb` reaches 0, `5*i + 1` alone visits every slot.
- **Deletion** marks the index slot as a dummy (a tombstone) and the entry as empty. A rebuild compacts empty entries. In GIL-enabled builds a later insertion can reuse a dummy index slot; free-threaded builds avoid that reuse for lookup safety.

## How Java's HashMap works

Java's `HashMap` uses separate chaining over an array whose length is always a power of two (default 16).

**Spreading the hash.** The bucket index is `(n − 1) & hash`: the low bits. To stop poor `hashCode()` implementations that differ only in their high bits from colliding, Java first mixes the high half into the low half:

```java
static int hash(Object key) {
  int h;
  return key == null ? 0
    : (h = key.hashCode()) ^ (h >>> 16);
}
```

**Resizing.** The default load factor is 0.75, so a 16-bucket table resizes when a 13th entry is added (threshold 12). It doubles. Because the size is a power of two, each entry in old bucket i goes either to bucket i or to bucket i + oldCapacity in the new table, depending on one bit of its hash (`hash & oldCap`). Java 8 uses this to split each chain into "low" and "high" lists in a single pass, preserving order.

**Tree bins (Java 8).** JEP 180 added protection against long chains. In OpenJDK 21, ordinary `put` invokes treeification when adding a ninth node to a chain of eight (`TREEIFY_THRESHOLD` is 8). Other insertion paths can reach the threshold differently. A tree bin gives logarithmic lookup when hashes or a consistent comparable-key order distinguish keys. Two conditions apply:

- If the whole table has fewer than **64** buckets (`MIN_TREEIFY_CAPACITY`), Java resizes the table instead, since a small table is the likelier cause of the long chain.
- When a resize splits a tree bin and a part has **6** or fewer entries (`UNTREEIFY_THRESHOLD`), it turns back into a list. The gap between 8 and 6 avoids flipping back and forth.

Tree nodes are ordered by hash, then by `compareTo` if the keys are `Comparable`. For keys with identical hashes that are not comparable, the tree cannot order them meaningfully, so the guarantee is weaker; `String` keys, the usual flooding target, are comparable.

> [!example] How rare are tree bins?
> The HashMap source notes that with random hash codes and a default maximum load factor of 0.75, bucket sizes follow a Poisson distribution with mean about 0.5. Under that approximate model, the probability of exactly 8 entries is about 0.00000006; this is not a measured treeification rate. Tree bins are a defence against bad or malicious hashes, not a normal-case optimisation.

**Pre-sizing.** `new HashMap<>(1000)` rounds the capacity up to 1,024, whose threshold is 768, so it still resizes once before reaching 1,000 entries. To hold n entries without resizing, the capacity must be at least n / 0.75. Java 19 added `HashMap.newHashMap(n)`, which does that calculation for you.

## Key takeaways
- Load factor α = n/m controls speed; tables resize when α passes a maximum (0.75 for Java's HashMap, about ⅔ for CPython's dict).
- Resizing rehashes every key, O(n), because bucket indices depend on m.
- Growing by a constant factor makes resizing overhead amortised O(1); constant increments give O(n) amortised copying cost. Hash collision costs are a separate assumption.
- CPython's dict uses a sparse index array over a dense, insertion-ordered entries array, with perturbed probing.
- Java's HashMap mixes high hash bits into low ones, splits chains on resize, and can convert long chains into red–black trees once the table has at least 64 buckets; ordinary OpenJDK 21 `put` invokes this on adding to a chain of eight.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
- [CPython dictobject.c source](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [More compact dictionaries with faster iteration — Raymond Hettinger, python-dev](https://mail.python.org/pipermail/python-dev/2012-December/123028.html)
- [HashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
- [JEP 180: Handle Frequent HashMap Collisions with Balanced Trees](https://openjdk.org/jeps/180)
