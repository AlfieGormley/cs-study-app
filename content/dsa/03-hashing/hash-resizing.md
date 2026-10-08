---
id: hash-resizing
title: Load factor and resizing
level: intermediate
minutes: 12
summary: Why tables grow at a fixed load factor, why doubling makes inserts amortised O(1), and how CPython's dict and Java's HashMap (with its Java 8 tree bins) actually work.
---

A hash table's speed depends on one ratio: how full it is. The **load factor** is

```formula
α = n / m
α = 12 / 16 = 0.75
where
α: alpha, the load factor: keys per bucket, a plain number with no unit
n: the number of keys stored, here 12
m: the number of buckets (slots) in the array, here 16
In words: divide the number of keys by the number of buckets; 12 keys in 16 buckets is a load factor of 0.75, exactly the point at which Java's HashMap grows.
```

Keep α low and buckets are mostly empty or hold a single key, so operations are fast. Let α creep up and chains lengthen or probe runs grow. Many dynamically growing tables therefore watch α and, when it passes a **maximum load factor**, allocate a bigger array and move everything across. This lesson is about that move: what it costs, why it is still cheap on average, and how two widely used implementations do it.

## Choosing the maximum load factor

The threshold is a space–time trade-off. A low maximum wastes memory on empty slots; a high one makes operations slower.

| Table | Typical/default growth policy | Scheme |
|---|---|---|
| Java `HashMap` | 0.75 | chaining |
| CPython `dict` | about 2/3 | open addressing |
| Abseil Swiss table | 7/8 | open addressing + SIMD |
| Redis dict | normally grows near 1; policy can defer growth | chaining |

Chaining tolerates a higher load factor because a slightly longer chain is a mild slowdown. Open addressing is far more sensitive. Knuth's classical estimate for a linear-probing miss (lesson 3) shows why:

```formula
P_miss ≈ ½ × (1 + 1 / (1 − α)^2)
α = 0.75:  P_miss ≈ ½ × (1 + 16) = 8.5
α = 0.875: P_miss ≈ ½ × (1 + 64) = 32.5
where
P_miss: the expected number of slots examined by an unsuccessful lookup in a linear-probing table
α: alpha, the load factor, the fraction of slots occupied; 0.875 is 7/8
½: one half
^: "to the power of"; (1 − α)^2 means (1 − α) × (1 − α)
≈: approximately equal to
In words: as the free fraction 1 − α shrinks, a miss costs about one over its square; going from 3/4 full to 7/8 full nearly quadruples the expected miss cost.
```

The formula assumes random hashing, plain linear probing and no deletions; it is not the formula for every probing design. Swiss tables can run at 7/8 full because they probe whole groups of slots at once, comparing one-byte metadata entries first, so few probes ever touch the slots themselves.

## Rehashing: why every key moves

When the table grows, you cannot copy the old array across as it is, because a key's bucket depends on the table size:

```formula
b = H mod m
b = 14 mod 4 = 2     (m = 4)
b = 14 mod 8 = 6     (m = 8)
where
b: the bucket index the key is stored in, from 0 to m − 1
H: the key's full hash value, which never changes; here 14
m: the number of buckets, 4 before growing and 8 after
mod: "modulo", the remainder after whole-number division
In words: the bucket is the hash's remainder after dividing by the table size, so changing the size moves the key; hash 14 lives in bucket 2 of 4 but bucket 6 of 8.
```

Doubling the table moves about half the keys under uniform hashing. Growing therefore means **rehashing**: walking every entry and inserting it into the new array.

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

Count the copying work for n inserts into a table that starts with one slot and doubles when full. Each resize copies every key present. First assume n is a power of two:

```formula
C = 1 + 2 + 4 + … + n / 2
C = n − 1 < n
C = 1 + 2 + 4 + … + 512 = 1023
where
C: the total number of key copies made by all the resizes together
n: the number of keys inserted, a power of two; here 1,024
…: "and so on", each term double the one before
<: "is less than"
In words: the resizes copy 1, then 2, then 4 keys and so on, and this doubling series always adds up to one less than n; inserting 1,024 keys causes only 1,023 copies in total, about one per insert.
```

The sum works because each term is bigger than all the earlier terms put together: the last resize does about half the total work. For powers of two this is fewer than n copies. For arbitrary n, the last copied capacity can exceed n/2, but the total is still fewer than 2n copies, or fewer than 3n units including placements. Thus **resizing overhead** is amortised O(1) per insert for every sequence. Overall hash-table insertion also depends on collision costs: the usual bound is expected amortised O(1), assuming well-distributed hashes and constant-time key operations.

Growing by a constant **amount** does not work. Add 10 slots each time and every resize copies 10 more keys than the last:

```formula
C ≈ 10 + 20 + 30 + … + n
C ≈ n^2 / 20
C ≈ 1000^2 / 20 = 50,000
where
C: the total number of key copies made by all the resizes
n: the number of keys inserted, here 1,000
…: "and so on", each term 10 more than the one before
^: "to the power of"; n^2 = n × n
≈: approximately equal to
In words: an arithmetic series of about n/10 resizes, averaging n/2 copies each, totals about n²/20; for 1,000 keys that is around 50,000 copies, about 50 per insert, and the per-insert cost keeps growing with n.
```

That is O(n) per insert, amortised. The program below counts the copies exactly (it starts at one slot, so its numbers differ slightly from the formula):

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

If a table also shrinks when it empties, do not use the same threshold in both directions. Grow when the table is completely full (load factor 1) and shrink when it drops below half full (load factor ½), and a workload hovering at the boundary (insert, delete, insert, …) would resize on every operation: a doubled table is exactly half full, so one delete shrinks it, and the shrunken table is full, so one insert doubles it again. The textbook fix is a **hysteresis gap** (a deliberate difference between the grow and shrink points): double when full, halve only when the load factor falls to ¼. After either resize the table is half full, so at least a quarter of its size in operations must happen before the next one. Many real tables simply never shrink automatically; CPython's dict does not shrink when you delete keys.

### When amortised is not good enough

Amortised O(1) still means an occasional O(n) pause. The pause depends on the implementation, key count, allocator and hardware; measure it against the server's latency budget.

**Incremental rehashing** spreads the work out. Redis keeps two tables during a resize and moves a few buckets on each operation (plus a little work in a background timer). Lookups check both tables until the move completes. Go's built-in map used a similar gradual "evacuation" before its Go 1.24 redesign. The cost is complexity and, temporarily, retaining both bucket arrays: when doubling, the old array plus one twice its size, so three times the old bucket count (excluding entries and other overhead).

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

- **Sizes** are powers of two, minimum 8, and a table holds at most about two-thirds of its size in entries (the formula below).
- **Growth**: when full, the new size is the smallest power of two that is at least 3 × the number of live keys. Without deletions this doubles the table: in CPython 3.14, a dict built key by key resizes on the 6th, 11th, 22nd and 43rd inserts.
- **Probing** uses a perturbed sequence, not linear steps. Starting from `i = hash & mask`, each step is `perturb >>= 5` then `i = (5*i + perturb + 1) & mask`. The shifting `perturb` feeds the high bits of the hash into the sequence, so keys that share low bits soon diverge; once `perturb` reaches 0, `5*i + 1` alone visits every slot.
- **Deletion** marks the index slot as a dummy (a tombstone) and the entry as empty. A rebuild compacts empty entries. In GIL-enabled builds a later insertion can reuse a dummy index slot; free-threaded builds avoid that reuse for lookup safety.

The size rules, written out (CPython's `USABLE_FRACTION` and growth calculation):

```formula
U = floor(2 × m / 3)
m_new = 2^⌈log_2(3 × u)⌉
U = floor(2 × 8 / 3) = floor(5.33) = 5
m_new = 2^⌈log_2(15)⌉ = 2^⌈3.91⌉
m_new = 2^4 = 16
where
U: the usable capacity: the most entries a table of size m can hold before it must grow
m: the table size (number of index slots), a power of two; here 8
m_new: the size of the new table after growing
u: the number of live keys when the table grows; here 5
floor: round down to a whole number
log_2: logarithm to base 2, the power 2 must be raised to; log_2(16) = 4, log_2(15) ≈ 3.91
⌈ ⌉: ceiling, round up to a whole number; ⌈3.91⌉ = 4
^: "to the power of"; 2^4 = 16
In words: a dict can fill two-thirds of its slots; when it is full it grows to the next power of two that is at least three times its live keys, so an 8-slot dict holds 5 keys and grows to 16 slots on the 6th insert.
```

And the probe sequence. Here `&` with `mask` (the table size minus 1) is the same as taking the remainder by the table size, and `perturb >>= 5` divides `perturb` by 32, rounding down:

```formula
i_0 = H mod m
q_new = floor(q / 32)
i_next = (5 × i + q_new + 1) mod m
where
i_0: the first slot tried
i: the slot just tried
i_next: the next slot to try
H: the key's full hash value
q: perturb, a value that starts equal to H and shrinks each step
q_new: perturb after shifting right by 5 bits
m: the table size, a power of two
mod: "modulo", the remainder after division
floor: round down to a whole number
In words: each step multiplies the current slot by 5, adds 1 plus the remaining high bits of the hash, and wraps round the table; the high bits shrink away after a few steps, leaving a sequence that visits every slot.
```

For example, with hash 1,234 in an 8-slot table: the first slot is 1,234 mod 8 = 2. Then perturb becomes 38 and the next slot is (10 + 38 + 1) mod 8 = 1; then perturb becomes 1 and the slot is (5 + 1 + 1) mod 8 = 7; then perturb is 0 and the slot is (35 + 1) mod 8 = 4.

## How Java's HashMap works

Java's `HashMap` uses separate chaining over an array whose length is always a power of two (default 16).

**Spreading the hash.** In Java's source the bucket index is `(n − 1) & hash`, where `n` is the table length (not the number of keys) and `&` is bitwise AND. Because the length is a power of two, this is the same as the remainder:

```formula
b = H mod m
b = 53 mod 16 = 5
where
b: the bucket index, from 0 to m − 1
H: the (spread) hash value of the key, here 53
m: the table length, a power of two; here 16
mod: "modulo", the remainder after division; for a power-of-two m it equals the low bits of H (53 is 110101 in binary, and its low four bits, 0101, are 5)
In words: Java keeps only the low bits of the hash, so a hash of 53 in a 16-bucket table goes to bucket 5.
```

Using only the low bits is fast, but it ignores the high bits. To stop poor `hashCode()` implementations that differ only in their high bits from colliding, Java first mixes the high half into the low half:

```java
static int hash(Object key) {
  int h;
  return key == null ? 0
    : (h = key.hashCode()) ^ (h >>> 16);
}
```

**Resizing.** Java resizes when the number of entries goes *above* a threshold:

```formula
T = C × L
T = 16 × 0.75 = 12
where
T: the threshold, the largest number of entries the table may hold before it doubles
C: the capacity, the number of buckets; here the default 16
L: the maximum load factor; here the default 0.75
In words: the threshold is buckets times the maximum load factor; a default map holds 12 entries and doubles when the 13th is added.
```

It doubles. Because the size is a power of two, each entry in old bucket i goes either to bucket i or to bucket i + oldCapacity in the new table, depending on one bit of its hash (`hash & oldCap`). Java 8 uses this to split each chain into "low" and "high" lists in a single pass, preserving order.

**Tree bins (Java 8).** JEP 180 added protection against long chains. In OpenJDK 21, ordinary `put` invokes treeification when adding a ninth node to a chain of eight (`TREEIFY_THRESHOLD` is 8). Other insertion paths can reach the threshold differently. A tree bin gives logarithmic lookup when hashes or a consistent comparable-key order distinguish keys. Two conditions apply:

- If the whole table has fewer than **64** buckets (`MIN_TREEIFY_CAPACITY`), Java resizes the table instead, since a small table is the likelier cause of the long chain.
- When a resize splits a tree bin and a part has **6** or fewer entries (`UNTREEIFY_THRESHOLD`), it turns back into a list. The gap between 8 and 6 avoids flipping back and forth.

Tree nodes are ordered by hash, then by `compareTo` if the keys are `Comparable`. For keys with identical hashes that are not comparable, the tree cannot order them meaningfully, so the guarantee is weaker; `String` keys, the usual flooding target, are comparable.

> [!example] How rare are tree bins?
> The HashMap source notes that with random hash codes and a default maximum load factor of 0.75, bucket sizes follow a **Poisson distribution** with mean about 0.5. Under that approximate model, the probability of exactly 8 entries is about 0.00000006 (worked out below); this is not a measured treeification rate. Tree bins are a defence against bad or malicious hashes, not a normal-case optimisation.

The Poisson distribution gives the chance of seeing exactly k events when they happen independently at an average rate λ. Here an "event" is a key landing in a particular bucket:

```formula
P(k) = e^(−λ) × λ^k / k!
P(8) = e^(−0.5) × 0.5^8 / 8!
P(8) = 0.6065 × 0.00390625 / 40320
P(8) ≈ 0.00000006
where
P(k): the probability that a given bucket holds exactly k entries
k: the number of entries in the bucket, here 8
λ: lambda, the average number of entries per bucket, here about 0.5
e: Euler's number, about 2.718; e^(−0.5) ≈ 0.6065
!: factorial, the product of all whole numbers up to that one; 8! = 8 × 7 × … × 1 = 40,320
^: "to the power of"
≈: approximately equal to
In words: with an average of half an entry per bucket, a bucket reaching 8 entries by chance happens about 6 times in 100 million buckets.
```

**Pre-sizing.** `new HashMap<>(1000)` rounds the capacity up to 1,024, whose threshold is 768, so it still resizes once before reaching 1,000 entries. To hold a given number of entries without resizing, the threshold must be at least that number:

```formula
C ≥ n / L
C ≥ 1000 / 0.75 = 1333.3
where
C: the capacity (buckets) to request, which Java rounds up to a power of two
n: the number of entries you plan to store, here 1,000
L: the maximum load factor, here the default 0.75
≥: "is at least"
In words: ask for at least the planned entry count divided by 0.75; 1,000 entries need a capacity of 1,334 or more, which Java rounds up to 2,048 buckets (threshold 1,536).
```

Java 19 added `HashMap.newHashMap(n)`, which does that calculation for you.

## Key takeaways
- The load factor (keys divided by buckets) controls speed; tables resize when it passes a maximum (0.75 for Java's HashMap, about ⅔ for CPython's dict).
- Resizing rehashes every key, O(n) for n keys, because bucket indices depend on the table size.
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
