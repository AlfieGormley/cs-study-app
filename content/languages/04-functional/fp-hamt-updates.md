---
id: fp-hamt-updates
title: Vector update allocation and HAMTs
level: advanced
minutes: 3
sourceLesson: fp-persistent-data
summary: Vector path copies allocate fixed-width arrays along the selected path.
---

Vector path copies allocate fixed-width arrays along the selected path. This unit develops that mechanism using the earlier units as prerequisites.

Updating index i uses path copying: copy each node on the path (each a 32-slot array) and change one slot:

```formula
M_path = L × 32 × 8 B
M_path = 4 × 32 × 8 B = 1024 B = 1 KiB
M_full = 10^6 × 8 B = 8 × 10^6 B = 8 MB
where
M_path: the memory allocated by one path-copying update, in bytes
M_full: the memory needed to copy a flat array of a million pointers, in bytes
L: the number of levels on the path, 4 for a million elements
32: the number of pointer slots in each copied node
8: the assumed pointer size for this worked model, in bytes; verify the actual ABI rather than inferring it from every use of the label 64-bit
B: bytes
KiB: kibibyte, exactly 1,024 bytes
MB: megabyte, a million bytes; payload counts exclude headers and allocator overhead
In words: an update copies one 32-pointer node per level, 1 KiB in this slot-payload model, instead of 8 MB for the whole array.
```

The flat pointer payload is 7,812.5 times the copied path payload in this model. Real object headers, allocation alignment, vector metadata, leaf representation and tail handling are excluded; this is not a measured allocation ratio.

One more trick makes appends fast. The vector keeps its last (up to) 32 elements in a separate **vector tail** array outside the tree. Most appends just copy that small tail; roughly once per 32 appends, a full tail is pushed into the tree when the next tail starts.

## Hash array mapped tries (HAMTs)

Maps and sets use the same shape keyed by hash. A common 32-way HAMT uses 5 hash bits per level. Bitmap nodes record occupied slots and compact their entries; implementations also use dense nodes and explicit hash-collision nodes. A child's position in the array is the number of set bits before its slot (a population-count operation, whose machine instructions depend on the target).

That compression matters: a conceptual sparse node with three child references needs three occupied child slots rather than thirty-two. Concrete HAMTs may store key/value pairs, tagged entries and extra metadata; Clojure bitmap nodes use alternating key/value-or-child slots.

HAMTs are everywhere once you look:

- Clojure's `PersistentHashMap` and `PersistentHashSet`
- Scala's immutable `HashMap` and `HashSet`
- Immutable.js `Map` (its `List` is a vector trie)
- Erlang and Elixir maps with more than 32 keys
- CPython's `contextvars`, which uses a HAMT internally so that copying a context is cheap

## Key takeaways
- Vector path copies allocate fixed-width arrays along the selected path.
- HAMT bitmaps compact occupied slots, with separate collision handling.

## Further reading
- [Clojure Vector](https://raw.githubusercontent.com/clojure/clojure/master/src/jvm/clojure/lang/PersistentVector.java)
- [Clojure Hamt](https://raw.githubusercontent.com/clojure/clojure/master/src/jvm/clojure/lang/PersistentHashMap.java)
- [Bagwell: Ideal Hash Trees](https://lampwww.epfl.ch/papers/idealhashtrees.pdf)
- [Pep567](https://peps.python.org/pep-0567/)
- [Erlang Maps](https://www.erlang.org/doc/system/maps.html)
- [Nist Binary](https://physics.nist.gov/cuu/Units/binary.html)
