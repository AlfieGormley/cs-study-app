---
id: adv-sparse-tables
title: Sparse tables, persistence and ropes
level: advanced
minutes: 14
summary: O(1) range-minimum queries with sparse tables, then a tour of persistent data structures built by path copying, and ropes for editing very long strings.
---

This lesson covers three ideas that share a theme: **trading how you store data for what you can ask of it**.

A sparse table spends O(n log n) memory on a static array so range-minimum queries become O(1). Balanced persistent trees using path copying can retain each version with O(log n) extra nodes per point update; persistence alone does not guarantee that bound. Ropes split a string into a tree of chunks so that inserting into the middle of a 100 MB document does not copy 100 MB.

## Range minimum queries

A **range minimum query** (RMQ) asks for the smallest value in `a[l..r]`. The options so far:

| Method | Build | Query | Updates |
|---|---|---|---|
| Scan | none | O(n) | O(1) |
| All pairs | O(n²) | O(1) | rebuild |
| Segment tree | O(n) | O(log n) | O(log n) |
| Sparse table | O(n log n) | O(1) | rebuild |

The sparse table is the right choice when the array **never changes** and there are many queries: for example, LCA queries on a fixed tree, or the LCP array of a suffix array.

## The sparse table

Precompute the minimum of every block whose length is a **power of two**. Entry `table[k][i]` holds `min(a[i .. i + 2^k − 1])`.

Each row comes from the row below it: a block of length 2^k is two blocks of length 2^(k−1) side by side.

```
table[k][i] = min(table[k-1][i],
                  table[k-1][i + 2^(k-1)])
```

```python
def build(a):
    n = len(a)
    table = [a[:]]
    j = 1
    while (1 << j) <= n:
        prev = table[-1]
        half = 1 << (j - 1)
        count = n - (1 << j) + 1
        row = [min(prev[i], prev[i + half])
               for i in range(count)]
        table.append(row)
        j += 1
    return table
```

There are about log2(n) + 1 rows of up to n entries, so the build is **O(n log n)** time and memory.

For `a = [5, 2, 4, 7, 1, 3, 6, 8]`:

```
k=0 (len 1): 5 2 4 7 1 3 6 8
k=1 (len 2): 2 2 4 1 1 3 6
k=2 (len 4): 2 1 1 1 1
k=3 (len 8): 1
```

### The O(1) query: overlap is fine

Any range of length L can be covered by **two** blocks of length 2^k, where 2^k is the largest power of two ≤ L. One starts at l and one ends at r. They may overlap in the middle.

```
query(2, 6), length 5, k = 2 (len 4):

index:  0 1 2 3 4 5 6 7
a:      5 2 4 7 1 3 6 8
            [-------]        a[2..5]
              [-------]      a[3..6]
min(1, 1) = 1
```

```python
def query(table, l, r):
    # min of a[l..r], inclusive
    k = (r - l + 1).bit_length() - 1
    return min(table[k][l],
               table[k][r - (1 << k) + 1])
```

Overlap does not matter for min, because counting an element twice does not change a minimum. The overlap query needs an associative combine that is also **idempotent**, meaning `f(x, x) = x`: min, max, gcd, bitwise AND and OR all qualify.

> [!warning] Sums are not idempotent
> Overlapping blocks would double-count the middle for a sum. You can still answer range sums from a sparse table in O(log n) by decomposing the range into **disjoint** power-of-two blocks (like a Fenwick prefix), but a prefix-sum array does that job in O(1) with O(n) memory. A **disjoint sparse table** stores the table differently to give O(1) queries for any associative operation.

`bit_length() - 1` computes floor(log2(L)). C++ code often uses `__builtin_clz` or precomputes a `log` array.

### Where it is used

- **Lowest common ancestor**: record an Euler tour of a tree (the nodes visited by a DFS, including returns) and their depths. The LCA of u and v is the shallowest node between their first appearances: an RMQ. O(n log n) build, O(1) per LCA.
- **Suffix arrays**: the longest common prefix of two distinct suffixes is the minimum of the LCP array between their positions, so an RMQ structure answers it in O(1).
- **Very large static data**: block decomposition schemes combine small in-block tables with a sparse table over block minima to get O(n) build and O(1) query. This is mostly of theoretical interest; in practice an O(n log n) table is usually fine.

## Persistent data structures

Ordinary structures are **ephemeral**: an update destroys the old version. A **persistent** structure keeps old versions usable. A **partially persistent** structure lets you read old versions; a **fully persistent** one lets you update them too, forming a tree of versions.

This sounds expensive, but most of each version is shared with the previous one.

### Path copying

In a tree, an update only changes nodes on one root-to-leaf path. Copy just those nodes, and point the copies at the **unchanged** subtrees of the old version:

```python
class T:
    __slots__ = ("key", "left", "right")
    def __init__(self, key, left=None,
                 right=None):
        self.key = key
        self.left = left
        self.right = right

def insert(t, key):
    # returns a new root; t is unchanged
    if t is None:
        return T(key)
    if key < t.key:
        return T(t.key, insert(t.left, key),
                 t.right)
    if key > t.key:
        return T(t.key, t.left,
                 insert(t.right, key))
    return t  # already present
```

Inserting 45 into the tree with keys 20, 30, 40, 50 and 70:

```
v1:     50          v2:     50'
       /  \                /  \
     30    70            30'   70 (shared)
    /  \                /  \
  20    40      (shared)20   40'
                               \
                                45 (new)
```

v2 created four nodes (50', 30', 40' and 45); everything else is shared. Both roots remain valid. In a balanced tree, each update costs **O(log n) time and memory**.

Other techniques:

- **Fat nodes**: each field stores a list of (version, value) pairs. Reads binary-search for the version. Good for partial persistence.
- **Driscoll, Sarnak, Sleator and Tarjan (1989)** showed how to make linked structures with a constant number of fields per node and bounded in-degree persistent with O(1) amortised extra space per primitive field-update step. A whole operation may contain many such steps.

### What persistence buys you

- **Cheap undo and snapshots**: retaining roots keeps historical nodes alive. Selecting a previous root is O(1), but storing history and reclaiming it have costs.
- **Safe sharing between threads**: immutable, safely published nodes need no mutation locks for readers. Publishing roots and keeping nodes alive still require the language's synchronisation and memory-reclamation rules.
- **Queries on history**: a **persistent segment tree** over value ranks, with one version per array prefix, answers "k-th smallest value in `a[l..r]`" in O(log n), by subtracting version l−1 from version r node by node.

### Where you meet it

- **Functional languages**: Haskell, Clojure, Scala and Erlang default to immutable collections. Clojure's vectors and maps are wide (32-way) trees with path copying, so updates copy about log32(n) nodes: around 6 levels for a billion elements.
- **Git**: a commit points to a tree of blobs. Changing one file creates new blob and tree objects up the path to the root; unchanged subtrees are shared by hash. That is path copying.
- **Databases and filesystems**: LMDB and Btrfs use copy-on-write trees. Retaining old pages supports snapshots; publication, reader coordination and page reclamation still follow each system's synchronisation rules.

> [!note] Persistence vs MVCC
> PostgreSQL's MVCC keeps old row versions for concurrent transactions, which is persistence at the row level, but it is not path copying: it keeps versions in the heap and cleans them up with VACUUM. LMDB's copy-on-write B-tree is the closer analogue.

## Ropes

A text editor holding a 100 MB file as one string must shift up to 100 MB of characters on every keystroke in the middle. A **rope** (Boehm, Atkinson and Plass, 1995) stores the text as a binary tree whose **leaves hold short string chunks**. Each internal node stores a **weight**: the total length of its left subtree.

```
            (9)
          /     \
       (6)       (2)
      /   \     /   \
 "Hello_" "my_" "na" "me_is_Simon"

text: Hello_my_name_is_Simon
```

### Indexing

To find character i, compare it with the weight: go left if smaller, otherwise subtract the weight and go right.

```python
class Leaf:
    def __init__(self, s):
        self.s = s
        self.length = len(s)

class Concat:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.weight = left.length
        self.length = (left.length
                       + right.length)

def char_at(node, i):
    if not 0 <= i < node.length:
        raise IndexError(i)
    while isinstance(node, Concat):
        if i < node.weight:
            node = node.left
        else:
            i -= node.weight
            node = node.right
    return node.s[i]
```

`char_at(root, 10)`: 10 ≥ 9, go right with i = 1; 1 < 2, go left; `"na"[1]` is `a`.

### Operations

| Operation | String | Balanced rope |
|---|---|---|
| Index | O(1) | O(log n) |
| Concatenate | O(n) | O(log n) |
| Insert m new characters | O(n + m) | O(log n + m) |
| Delete a range | O(n) | Implementation-dependent |
| Iterate all | O(n) | O(n) |

These bounds assume balanced trees and bounded leaf sizes. Inserting new text must read/copy its m characters; deletion can also incur work to reclaim removed nodes. Concatenation creates a new root over two ropes, then rebalances. Insert is **split** at the position, then two concatenations. Ropes are usually built from immutable nodes, so they are persistent for free: undo history costs only the changed paths.

### Real-world use

- **Editors**: the Xi editor and Zed use rope-like B-trees of text chunks. VS Code instead uses a **piece table** stored in a red–black tree (the "piece tree"), which records edits as references into the original file and an append-only buffer. Both avoid copying the document on each keystroke.
- **Libraries**: the SGI STL shipped `rope`, and Rust crates such as `ropey` provide them.

Ropes are not always better. For short strings, the pointer overhead and lost cache locality make them slower than a flat array. Leaves are therefore usually hundreds of bytes to a few kilobytes, so most work is still done on contiguous memory.

## Pitfalls

- **Sparse tables on changing data**: a point update can affect O(n) blocks across all levels, because the number at level k is at most 2^k. Use a segment tree instead.
- **Using the overlap trick for sums**: it double-counts. The combine must be associative and idempotent.
- **Mutating a "persistent" node**: one in-place write corrupts every version sharing that node. Persistence relies on discipline or immutable types.
- **Unbalanced ropes**: repeated appends without rebalancing make a chain with O(n) indexing.

## Key takeaways
- A sparse table stores minima of all power-of-two blocks: O(n log n) build, O(1) queries by covering the range with two overlapping blocks.
- The overlap trick needs an associative, idempotent operation (min, max, gcd, AND, OR). Sums need disjoint blocks or prefix sums.
- Path copying makes balanced trees persistent at O(log n) extra space per update, by copying one path and sharing the rest. Git, Clojure and copy-on-write B-trees work this way.
- A rope is a weighted tree of string chunks, giving logarithmic tree navigation when balanced; insertion also costs O(m) for m new characters, and deletion costs depend on reclamation.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
