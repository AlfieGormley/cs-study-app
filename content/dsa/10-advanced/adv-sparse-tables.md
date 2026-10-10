---
id: adv-sparse-tables
title: Sparse tables, persistence and ropes
level: advanced
minutes: 14
summary: O(1) range-minimum queries with sparse tables, then an overview of persistent data structures built by path copying, and ropes for editing very long strings.
---

This lesson covers three ideas that share a theme: **trading how you store data for what you can ask of it**.

Throughout, n is the number of items stored (array elements, tree keys or characters), and O(f) means "grows at most in proportion to f" (big-O notation). A sparse table spends O(n log n) memory on a static array so range-minimum queries become O(1), constant time whatever the range. Balanced persistent trees using path copying can retain each version with O(log n) extra nodes per point update; persistence alone does not guarantee that bound. Ropes split a string into a tree of chunks so that inserting into the middle of a 100 MB document does not copy 100 MB.

## Range minimum queries

A **range minimum query** (RMQ) asks for the smallest value in `a[l..r]`, the elements from index l to index r inclusive. The options so far, for an array of n elements (O(n²) means growing with n × n):

| Method | Build | Query | Updates |
|---|---|---|---|
| Scan | none | O(n) | O(1) |
| All pairs | O(n²) | O(1) | rebuild |
| Segment tree | O(n) | O(log n) | O(log n) |
| Sparse table | O(n log n) | O(1) | rebuild |

The sparse table is the right choice when the array **never changes** and there are many queries: for example, LCA queries on a fixed tree, or the LCP array of a suffix array.

## The sparse table

Precompute the minimum of every block whose length is a **power of two** (1, 2, 4, 8, …). Row k of the table holds the minima of all blocks of length 2 to the power k, and each row comes from the row below it, because a block of length 2^k is two blocks of half that length side by side:

```formula
T[0][i] = a[i]
T[k][i] = min(T[k−1][i], T[k−1][i + h])
h = 2^{k−1}
T[1][3] = min(T[0][3], T[0][4])
T[1][3] = min(7, 1) = 1
where
a: the input array, which never changes
a[i]: the element of a at index i, counting from 0
i: the start index of a block
k: the row number; row k holds blocks of length 2^k
2^k: k copies of 2 multiplied together, the block length in row k (2^0 = 1)
T[k][i]: the table entry for row k, index i: the minimum of a[i] through a[i + 2^k − 1]
h: the half-block length, 2 to the power k − 1
min(x, y): the smaller of x and y
In words: the minimum of a block is the smaller of the minima of its left half and its right half, so each row is built from the row below in one pass.
```

The worked lines use the example array below, `a = [5, 2, 4, 7, 1, 3, 6, 8]`: the length-2 block starting at index 3 covers 7 and 1, so its minimum is 1. The recurrence only works for operations where combining two halves gives the answer for the whole, which holds for min.

The code builds row after row (`table` is T, `j` is k and `half` is h):

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

Each row fits as long as its block length is at most n, which fixes how many rows there are and bounds the size:

```formula
R = ⌊log_2(n)⌋ + 1
S ≤ n × R
R = ⌊log_2(8)⌋ + 1 = 4
S = 8 + 7 + 5 + 1 = 21 ≤ 32
R = ⌊log_2(10^6)⌋ + 1 = 20
S ≤ 10^6 × 20 = 2 × 10^7
where
n: the number of elements in the array
R: the number of rows in the sparse table
S: the total number of table entries
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌊ ⌋: floor: round down to the nearest whole number
≤: is at most
In words: there is one row for each power of two up to n, and each row holds at most n entries, so the table holds at most n times (log_2(n) + 1) entries.
```

The 8-element example below has 4 rows and 21 entries. A million elements need at most 20 million entries, about 80 MB as 4-byte integers (the exact count, about 18.95 million entries, is about 76 MB), and far more as Python objects. So the build is **O(n log n)** time and memory, and that memory is the main limit on how large an array a sparse table suits.

For `a = [5, 2, 4, 7, 1, 3, 6, 8]`:

```
k=0 (len 1): 5 2 4 7 1 3 6 8
k=1 (len 2): 2 2 4 1 1 3 6
k=2 (len 4): 2 1 1 1 1
k=3 (len 8): 1
```

### The O(1) query: overlap is fine

Any range can be covered by **two** blocks of the same power-of-two length: the largest power of two that fits inside the range. One block starts at the left end and one ends at the right end. They may overlap in the middle.

```formula
L = r − l + 1
k = ⌊log_2(L)⌋
q = min(T[k][l], T[k][r − 2^k + 1])
L = 6 − 2 + 1 = 5
k = ⌊log_2(5)⌋ = 2
q = min(T[2][2], T[2][3]) = min(1, 1) = 1
where
l: the left end of the query range (an index, inclusive)
r: the right end of the query range (an index, inclusive)
L: the length of the range, in elements
k: the row to use: the largest whole number with 2^k ≤ L
2^k: k copies of 2 multiplied together, the length of each of the two blocks
T[k][i]: the sparse-table entry: the minimum of the length-2^k block starting at index i
q: the answer, the minimum of a[l] through a[r]
log_2(L): the base-2 logarithm of L
⌊ ⌋: floor: round down to the nearest whole number
min(x, y): the smaller of x and y
≤: is at most
In words: pick the biggest power-of-two block that fits in the range, take one starting at the left end and one ending at the right end, and the smaller of their two minima is the range minimum.
```

The worked lines are `query(2, 6)` on the example array: two length-4 blocks, a[2..5] and a[3..6], overlapping at indices 3 to 5:

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

Overlap does not matter for min, because counting an element twice does not change a minimum. The overlap query needs an associative combine that is also an **idempotent operation**: combining a value with itself gives the value back.

```formula
f(x, x) = x
min(7, 7) = 7
7 + 7 = 14
where
f: the combining operation (min, max, gcd, AND, OR, +, …)
x: any value
min(x, y): the smaller of x and y
In words: an operation is idempotent when applying it to two copies of the same value just gives that value; min is, addition is not.
```

Min, max, gcd (greatest common divisor), bitwise AND and bitwise OR all qualify.

> [!warning] Sums are not idempotent
> Overlapping blocks would double-count the middle for a sum. You can still answer range sums from a sparse table in O(log n), with n the array length, by decomposing the range into **disjoint** power-of-two blocks (like a Fenwick prefix), but a prefix-sum array does that job in O(1) with O(n) memory. A **disjoint sparse table** stores the table differently to give O(1) queries for any associative operation.

In the Python, `bit_length() - 1` computes k, the base-2 logarithm of the range length rounded down: 5 is `101` in binary, 3 bits long, so k is 2. C++ code often uses `__builtin_clz` or precomputes a `log` array.

### Where it is used

- **Lowest common ancestor**: record an Euler tour of a tree (the nodes visited by a DFS, including returns) and their depths. The LCA of u and v is the shallowest node between their first appearances: an RMQ. For a tree of n nodes (the Euler tour has 2n − 1 entries), that is O(n log n) build and O(1) per LCA.
- **Suffix arrays**: the longest common prefix of two distinct suffixes is the minimum of the LCP array between their positions, so an RMQ structure answers it in O(1).
- **Very large static data**: block decomposition schemes combine small in-block tables with a sparse table over block minima to get O(n) build and O(1) query, where n is the array length. This is mostly of theoretical interest; in practice an O(n log n) table is usually fine.

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

v2 created four nodes (50', 30', 40' and 45); everything else is shared. Both roots remain valid. In a balanced tree, the copied path is only as long as the tree is tall:

```formula
p ≈ log_2(n)
p ≈ log_2(10^6) ≈ 20
where
p: the number of nodes copied by one insert (the root-to-leaf path)
n: the number of keys in the balanced tree
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≈: approximately equal to
In words: one insert copies about as many nodes as the tree has levels, which grows with the logarithm of the number of keys.
```

So each update costs **O(log n) time and memory**: about 20 new nodes per insertion into a million-key tree, instead of copying a million. This only holds if the tree stays balanced; a badly unbalanced tree would copy a path as long as the whole chain.

Other techniques:

- **Fat nodes**: each field stores a list of (version, value) pairs. Reads binary-search for the version. Good for partial persistence.
- **Driscoll, Sarnak, Sleator and Tarjan (1989)** showed how to make linked structures with a constant number of fields per node and bounded in-degree persistent with O(1) amortised extra space per primitive field-update step. A whole operation may contain many such steps.

### What persistence buys you

- **Cheap undo and snapshots**: retaining roots keeps historical nodes alive. Selecting a previous root is O(1), but storing history and reclaiming it have costs.
- **Safe sharing between threads**: immutable, safely published nodes need no mutation locks for readers. Publishing roots and keeping nodes alive still require the language's synchronisation and memory-reclamation rules.
- **Queries on history**: a **persistent segment tree** over value ranks, with one version per array prefix, answers "k-th smallest value in `a[l..r]`" in O(log n), with n the array length. It subtracts one version's counts from another's, node by node (shown below).

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

- **Functional languages**: Haskell, Clojure, Scala and Erlang default to immutable collections. Clojure's vectors and maps are wide (32-way) trees with path copying, so an update copies one node per level:

```formula
d = log_32(n) = log_2(n) / 5
d = log_32(10^9) ≈ 29.9 / 5 ≈ 6
where
d: the number of levels in the tree, and so the nodes copied per update
n: the number of elements in the collection
log_32(n): the base-32 logarithm of n: the power you raise 32 to in order to get n
log_2(n): the base-2 logarithm of n; dividing by 5 converts it because 32 = 2^5
≈: approximately equal to
In words: a 32-way tree is about a fifth as tall as a binary tree, so a billion elements need only about 6 levels.
```

  Each copied node is a 32-slot array, so an update still copies about 6 × 32 pointers rather than 6.
- **Git**: a commit points to a tree of blobs. Changing one file creates new blob and tree objects up the path to the root; unchanged subtrees are shared by hash. That is path copying.
- **Databases and filesystems**: LMDB and Btrfs use copy-on-write trees. Retaining old pages supports snapshots; publication, reader coordination and page reclamation still follow each system's synchronisation rules.

> [!note] Persistence vs MVCC
> PostgreSQL's MVCC keeps old row versions for concurrent transactions, which is persistence at the row level, but it is not path copying: it keeps old row versions in the table's own storage and cleans them up with VACUUM. LMDB's copy-on-write B-tree is the closer analogue.

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

Tracing `char_at(root, 10)` on the rope above:

```formula
i = 10,   w_root = 9
i ≥ w_root,   so i = 10 − 9 = 1
i = 1 < w_right = 2
c = "na"[1] = "a"
where
i: the index of the wanted character, counting from 0 within the current subtree
w_root: the root's weight: the length of its left subtree, 6 + 3 = 9 characters
w_right: the weight of the root's right child: the length of "na", 2 characters
c: the character found
≥: is at least
<: is less than
In words: at the root the index is not below the weight, so go right and subtract the 9 skipped characters; at the next node 1 is below the weight 2, so go left to the leaf "na", whose character 1 is "a".
```

Character 10 of `Hello_my_name_is_Simon` is indeed `a`. The cost is one step per level, so a balanced rope finds any character in O(log n) steps for n characters.

### Operations

Here n is the length of the text in characters and m the number of characters inserted:

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

- **Sparse tables on changing data**: a point update can affect O(n) blocks across all levels, where n is the array length. Use a segment tree instead. The count adds up like this:

```formula
B_k ≤ 2^k
B ≤ 2^0 + 2^1 + … + 2^K = 2^{K+1} − 1
B ≤ 2^{K+1} − 1 < 2 × n
K = ⌊log_2(n)⌋
where
k: a row of the sparse table, holding blocks of length 2^k
B_k: how many blocks in row k contain the changed element
K: the top row number
B: the total number of entries that must be recomputed
n: the array length
2^k: k copies of 2 multiplied together
log_2(n): the base-2 logarithm of n
⌊ ⌋: floor: round down to the nearest whole number
≤: is at most
<: is less than
In words: each row has at most block-length many blocks covering the element, and those block lengths add up to less than twice n.
```

  For a million elements K is 19, so one change can touch up to 2^20 − 1 = 1,048,575 entries, about a million, against about 20 nodes in a segment tree.
- **Using the overlap trick for sums**: it double-counts. The combine must be associative and idempotent.
- **Mutating a "persistent" node**: one in-place write corrupts every version sharing that node. Persistence relies on discipline or immutable types.
- **Unbalanced ropes**: repeated appends without rebalancing make a chain with O(n) indexing, where n is the number of leaves.

## Key takeaways
- A sparse table over n elements stores minima of all power-of-two blocks: O(n log n) build, O(1) queries by covering the range with two overlapping blocks.
- The overlap trick needs an associative, idempotent operation (min, max, gcd, bitwise AND, bitwise OR). Sums need disjoint blocks or prefix sums.
- Path copying makes balanced trees of n keys persistent at O(log n) extra space per update, by copying one path and sharing the rest. Git, Clojure and copy-on-write B-trees work this way.
- A rope is a weighted tree of string chunks, giving logarithmic tree navigation when balanced; insertion also costs O(m) for m new characters, and deletion costs depend on reclamation.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
