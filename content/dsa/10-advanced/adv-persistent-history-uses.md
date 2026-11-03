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
- Queries on history: a **persistent segment tree** over value ranks, with one version per array prefix, answers "k-th smallest value in `a[l..r]`" in O(log n), with n the array length. It subtracts one version's counts from another's, node by node (explained below).

Take the count in the version through the range's right endpoint and subtract the count in the version just before its left endpoint. At each value-tree node, that difference counts only elements from the requested slice. To find a requested rank, go left if its count reaches the rank; otherwise subtract that count and continue right.

For example, `a = [5, 2, 4, 7]` and v covers the values 1 to 4: the four elements a[0..3] contain two such values (2 and 4), a[0] contains none, so the slice a[1..3] has 2. It needs an unchanged array; changing an element would change every later version.

### Where you meet it

- **Functional languages**: Haskell, Clojure, Scala and Erlang default to immutable collections. Clojure’s vectors use a wide branching tree plus a tail buffer; hash maps use hash-array mapped tries with collision handling and specialised small forms. Path copying shares unchanged structure. Their wide branching reduces height:

Wide branching makes the tree shallower, but copying an array node also copies its child references. Actual costs depend on occupied branches, tail buffers and hash collisions, rather than one universal node count.


- **Git**: a commit points to a tree of blobs. Changing one file creates new blob and tree objects up the path to the root; unchanged subtrees are shared by hash. That is path copying.
- Databases and filesystems: LMDB and Btrfs use copy-on-write trees. Retaining old pages supports snapshots; publication, reader coordination and page reclamation still follow each system's synchronisation rules.

> [!note] Persistence vs MVCC
> PostgreSQL's MVCC keeps old row versions for concurrent transactions, which is persistence at the row level, but it is not path copying: it keeps old row versions in the table's own storage and cleans them up with VACUUM. LMDB's copy-on-write B-tree is the closer analogue.

## Key takeaways

- Subtract two prefix versions’ counts to query one array slice.
- Root publication and memory reclamation still need coordination even when nodes are immutable.

## Further reading
- [Making Data Structures Persistent — Driscoll, Sarnak, Sleator and Tarjan](https://www.cs.cmu.edu/~sleator/papers/making-data-structures-persistent.pdf)
- [Git objects and shared trees](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [PostgreSQL row-version maintenance](https://www.postgresql.org/docs/current/routine-vacuuming.html)
