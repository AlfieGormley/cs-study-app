---
id: fp-vector-indexing
title: Wide vector tries and index digits
level: advanced
minutes: 3
sourceLesson: fp-persistent-data
summary: Five-bit index chunks select among 32 child slots.
---

Five-bit index chunks select among 32 child slots. This unit develops that mechanism using the earlier units as prerequisites.

## Wide trees: the 32-way trie

A balanced binary tree can require about 20 dependent node accesses for a million keys; cache behavior depends on layout and workload. Wide tries reduce depth.

## Persistent vectors

Clojure's `PersistentVector` (designed by Rich Hickey, building on Phil Bagwell's work) uses internal nodes with up to **32 child slots**. To find index i, split i into 5-bit chunks (2⁵ = 32) and use each chunk to pick a child:

```
index 1000: 0b 00000 11111 01000
               level0 level1 leaf
                0      31     8
```

This diagram shows conceptual base-32 digits with a leading zero group. The actual number of root levels depends on the vector size and its tail; the leading zero does not require an extra node in every implementation. Each chunk is one digit of the index written in base 32:

```formula
i = c_0 32^2 + c_1 32 + c_2
1000 = 0 × 1024 + 31 × 32 + 8
where
i: the element's index (position) in the vector, here 1000
c_0, c_1, c_2: the three 5-bit chunks of i, from the top level down to the leaf; each is a whole number from 0 to 31 that picks one of 32 child slots
32: the branching factor: each node has up to 32 children, and 32 = 2^5, so one chunk is exactly 5 bits
32^2: 32 × 32 = 1,024
In words: reading the index 5 bits at a time gives the slot to follow at each level: slot 0 at the top, slot 31 in the middle, slot 8 in the leaf.
```

Ignoring tail optimization and partially filled roots, the number of array levels is the base-32 logarithm of n, rounded up:

```formula
L = ⌈log_32(n)⌉
L = ⌈log_32(1000000)⌉ = ⌈3.99⌉ = 4
L = ⌈log_32(10^9)⌉ = ⌈5.98⌉ = 6
where
L: the number of levels of 32-slot arrays from the root to the elements
n: the positive number of elements in this simplified model; take at least two elements so a one-element special case does not need a separate convention
log_32(n): the base-32 logarithm of n: how many times you can divide n by 32 before reaching 1
⌈ ⌉: the ceiling: round up to the next whole number
In words: each level multiplies capacity by 32, so the level count grows extremely slowly: a million elements need 4 levels, a billion need 6.
```

| Elements | Levels |
|---|---|
| 32 | 1 |
| 1,024 | 2 |
| 32,768 | 3 |
| ~1 million | 4 |
| ~1 billion | 6 |

Six hops for a billion elements is why people call these operations "effectively constant". They are still O(log n), but the base is 32.

## Key takeaways
- Five-bit index chunks select among 32 child slots.
- A simplified full trie model explains slowly growing depth.

## Further reading
- [Clojure Vector](https://raw.githubusercontent.com/clojure/clojure/master/src/jvm/clojure/lang/PersistentVector.java)
- [Clojure Data](https://clojure.org/reference/data_structures)
