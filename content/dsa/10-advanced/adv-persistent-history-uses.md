---
id: adv-persistent-history-uses
title: Historical queries and persistent systems
level: advanced
minutes: 4
summary: Subtract two prefix versions’ counts to query one array slice.
sourceLesson: adv-sparse-tables
---

Here n is the array length, tree size or text length specified in the section. Big-O costs assume fixed-size summaries and constant-time word operations.

### What persistence buys you

- Cheap undo and snapshots: retaining roots keeps historical nodes alive. Selecting a previous root is O(1), but storing history and reclaiming it have costs.
- Safe sharing between threads: immutable, safely published nodes need no mutation locks for readers. Publishing roots and keeping nodes alive still require the language's synchronisation and memory-reclamation rules.
- Queries on history: a **persistent segment tree** over value ranks, with one version per array prefix, answers "k-th smallest value in `a[l..r]`" in O(log n), with n the array length. It subtracts one version's counts from another's, node by node (shown below).

```formula
C(l, r, v) = c_r(v) − c_{l−1}(v)
C(1, 3, v) = c_3(v) − c_0(v)
C(1, 3, v) = 2 − 0 = 2
where
v: a node of the segment tree, covering a range of values
l: the left end of the query range (an array index, from 0)
r: the right end of the query range (inclusive)
c_r(v): in the version built from a[0] through a[r], how many of those elements have a value in v's range
c_{l−1}(v): the same count in the version built from a[0] through a[l − 1] (zero when l is 0)
C(l, r, v): how many of a[l] through a[r] have a value in v's range
c_3, c_0: the counts c_r with r = 3 (version after a[0..3]) and r = 0 (version after a[0] only)
In words: the count of values in a range of the array is the count up to its right end minus the count before its left end, so two versions together act like a segment tree of just that slice.
```

In the worked lines, `a = [5, 2, 4, 7]` and v covers the values 1 to 4: the four elements a[0..3] contain two such values (2 and 4), a[0] contains none, so the slice a[1..3] has 2. Walking down, the query goes left when the left child's count is at least k and right otherwise. It needs a static array; changing an element would change every later version.

### Where you meet it

- **Functional languages**: Haskell, Clojure, Scala and Erlang default to immutable collections. Clojure’s vectors use a wide branching tree plus a tail buffer; hash maps use hash-array mapped tries with collision handling and specialised small forms. Path copying shares unchanged structure. For an idealised full 32-way tree, the height estimate is:

```formula
d_model = log_32(n) = log_2(n) / 5
d_model = log_32(10^9) ≈ 29.9 / 5 ≈ 6
where
d_model: a logarithm-based height estimate for an idealised full 32-way tree, not an exact count of Clojure nodes copied
n: the number of elements in the collection
log_32(n): the base-32 logarithm of n: the power you raise 32 to in order to get n
log_2(n): the base-2 logarithm of n; dividing by 5 converts it because 32 = 2^5
≈: approximately equal to
In words: a 32-way tree is about a fifth as tall as a binary tree, so a billion elements need only about 6 levels.
```

  In a model of full-width array nodes, copying six 32-slot nodes moves roughly 192 references. Actual Clojure copies depend on tails, occupied branches and hash collisions; this is not a universal copy count.
- **Git**: a commit points to a tree of blobs. Changing one file creates new blob and tree objects up the path to the root; unchanged subtrees are shared by hash. That is path copying.
- Databases and filesystems: LMDB and Btrfs use copy-on-write trees. Retaining old pages supports snapshots; publication, reader coordination and page reclamation still follow each system's synchronisation rules.

> [!note] Persistence vs MVCC
> PostgreSQL's MVCC keeps old row versions for concurrent transactions, which is persistence at the row level, but it is not path copying: it keeps old row versions in the table's own storage and cleans them up with VACUUM. LMDB's copy-on-write B-tree is the closer analogue.

## Key takeaways

- Subtract two prefix versions’ counts to query one array slice.
- Root publication and memory reclamation still need coordination even when nodes are immutable.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
