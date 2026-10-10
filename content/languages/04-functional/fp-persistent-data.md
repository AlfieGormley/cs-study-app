---
id: fp-persistent-data
title: Persistent data structures
level: advanced
minutes: 14
summary: How immutable lists, trees, maps and vectors make cheap "modified copies" by sharing structure, the 32-way tries behind Clojure, Scala and Immutable.js, and the traps where persistence breaks amortised bounds.
---

Immutability has an obvious cost. If you can never change a list in place, then "add one element" seems to mean "copy the whole list and add one element". Do that in a loop over a million items and you've written an O(n²) algorithm, where n is the number of items: each step copies everything added so far.

```formula
0 + 1 + 2 + ... + (n − 1) = n × (n − 1) / 2
n × (n − 1) / 2 = O(n^2)
where
n: the number of items added, one per loop step
...: "and so on" for every step in between
O(n^2): Big-O notation: grows in proportion to n squared (n × n)
In words: the k-th step copies the k − 1 items already there, and those copies add up to about half of n squared.
```

For n = 1,000,000 that is about 500 billion item copies (1,000,000 × 999,999 / 2, roughly 5 × 10¹¹).

Efficient persistent collections reduce that cost through sharing. **Persistence** means: every "update" returns a new version, the old version stays valid, and the two **share almost all of their memory**. Only the small part that actually changed is new.

This lesson shows how that works, from the humble linked list up to the 32-way tries that power Clojure's vectors and maps, and where the trick stops being free.

## What "persistent" means

Here *persistent* has nothing to do with disks. It means old versions persist after an update.

| Kind | Old versions can be |
|---|---|
| Ephemeral (normal) | gone after update |
| Partially persistent | read, not updated |
| Fully persistent | read and updated |
| Confluent | merged with each other |

Purely functional structures are fully persistent automatically: nothing is ever mutated, so every version you hold a reference to is still intact and can be the starting point of new updates.

The naive way to get this is to copy everything on every update. The real way is **structural sharing**.

## The linked list: sharing for free

The singly linked list (a *cons list*) is the simplest persistent structure. Each cell holds a value and a pointer to the rest:

```python
xs = (3, None)
ys = (2, xs)       # [2, 3]
a  = (1, ys)       # [1, 2, 3]
b  = (9, ys)       # [9, 2, 3]

a[1] is b[1]       # True: shared tail
```

```
a --> [1|*]--+
             v
           [2|*]--> [3|/]
             ^
b --> [9|*]--+
```

Prepending to a list allocates one cell and points it at the old list. It's O(1) time and space, and the old list is untouched. That's why Haskell, Lisp, Erlang and Elixir lists grow at the front.

The costs show up at the other end. In this table n is the list's length and i is the position being read or changed (0 for the first cell). O(1) means a fixed cost however long the list is; O(n) and O(i) mean a cost in proportion to n or i:

| Operation | Cost | Why |
|---|---|---|
| Prepend | O(1) | new head, shared tail |
| Head / tail | O(1) | follow one pointer |
| Append | O(n) | copy every cell |
| Index i | O(i) | walk i pointers |
| Update at i | O(i) | copy cells 0..i |

Appending must copy every cell, because the last cell's pointer has to change and every cell before it points (indirectly) at that one. For this immutable linked-list path-copying approach, copy the prefix leading to the change; persistence in general has other implementation techniques.

## Trees: path copying

That rule gives the key technique for trees. To change a leaf of a tree, copy **only the nodes on the path from the root to it**. Every subtree off that path is reused by pointer.

Inserting 65 into a binary search tree:

```
version 1:
        50
       /  \
     30    70
    /  \   / \
   20  40 60  80

version 2 (after inserting 65):
        50'
       /  \
    (30)   70'
           / \
         60'  (80)
           \
            65
```

Nodes marked `'` are new copies, and 65 is the new leaf. `(30)` (with its whole subtree) and `(80)` are the very same objects as in version 1, reached by pointer. Here's the whole thing in Python:

```python
from typing import NamedTuple

class Node(NamedTuple):
    key: int
    left: "Node | None"
    right: "Node | None"

def insert(t, k):
    if t is None:
        return Node(k, None, None)
    if k < t.key:
        return t._replace(
            left=insert(t.left, k))
    if k > t.key:
        return t._replace(
            right=insert(t.right, k))
    return t
```

`_replace` builds a new node with one field changed. The new version shares the whole left subtree:

```python
v2 = insert(v1, 65)
v2.left is v1.left        # True
v2.right.right is v1.right.right  # True
```

For a **balanced tree** (one whose branches all have roughly the same depth) of n keys, the path has about log₂ n nodes:

```formula
h ≈ log_2(n)
h ≈ log_2(1000000) ≈ 19.9 ≈ 20
where
h: the height of the tree: the number of nodes on a path from the root to a leaf, and so the number of nodes an insert copies
n: the number of keys in the tree
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1 (2^20 = 1,048,576)
≈: approximately equal to
In words: each level of a balanced binary tree doubles how many keys it can hold, so a million keys needs only about 20 levels.
```

With a million keys that's about 20 new nodes per insert, instead of a million. Both versions remain fully usable, and the extra memory is O(log n) per update: it grows with the logarithm of n, not with n itself. The figure only holds while the tree stays balanced; a tree built by inserting sorted keys without rebalancing degenerates into a list with height n.

This is how Haskell's `Data.Map` and `Data.Set` (size-balanced binary trees), OCaml's `Map`, and Scala's `TreeMap` work. Rebalancing (rotations in a red-black or AVL tree) only touches nodes near the path, so it stays O(log n).

> [!example] Git does this too
> A Git commit points to a tree object for the root directory, which points to trees and blobs for its contents. Change one file and Git writes a new blob, new trees for each directory on the path up to the root, and a new commit. Every unchanged directory is shared with the previous commit by hash. That's path copying on your file system.

## Wide trees: the 32-way trie

A balanced binary tree can require about 20 dependent node accesses for a million keys; cache behavior depends on layout and workload. Wide tries reduce depth.

### Persistent vectors

Clojure's `PersistentVector` (designed by Rich Hickey, building on Phil Bagwell's work) uses internal nodes with up to **32 child slots**. To find index i, split i into 5-bit chunks (2⁵ = 32) and use each chunk to pick a child:

```
index 1000 = 0b 00000 11111 01000
               level0 level1 leaf
                0      31     8
```

Each chunk is one digit of the index written in base 32:

```formula
i = c_0 × 32^2 + c_1 × 32 + c_2
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
n: the number of elements in the vector
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

Updating index i uses path copying: copy each node on the path (each a 32-slot array) and change one slot:

```formula
M_path = L × 32 × 8 B
M_path = 4 × 32 × 8 B = 1024 B ≈ 1 KB
M_full = 10^6 × 8 B = 8 × 10^6 B = 8 MB
where
M_path: the memory allocated by one path-copying update, in bytes
M_full: the memory needed to copy a flat array of a million pointers, in bytes
L: the number of levels on the path, 4 for a million elements
32: the number of pointer slots in each copied node
8: the size of one pointer on a 64-bit machine, in bytes
B: bytes
KB: kilobyte, about a thousand bytes
MB: megabyte, a million bytes
In words: an update copies one 32-pointer node per level, about 1 KB in total, instead of 8 MB for the whole array.
```

That's about 8,000 times less memory per update (plus small per-object headers, which the formula ignores).

One more trick makes appends fast. The vector keeps its last (up to) 32 elements in a separate **tail** array outside the tree. Most appends just copy that small tail; roughly once per 32 appends, a full tail is pushed into the tree when the next tail starts.

### Hash array mapped tries (HAMTs)

Maps and sets use the same shape keyed by hash. A common 32-way HAMT uses 5 hash bits per level. Bitmap nodes record occupied slots and compact their entries; implementations also use dense nodes and explicit hash-collision nodes. A child's position in the array is the number of set bits before its slot (a population-count operation, whose machine instructions depend on the target).

That compression matters: a sparse node with 3 children stores 3 pointers, not 32.

HAMTs are everywhere once you look:

- Clojure's `PersistentHashMap` and `PersistentHashSet`
- Scala's immutable `HashMap` and `HashSet`
- Immutable.js `Map` (its `List` is a vector trie)
- Erlang and Elixir maps with more than 32 keys
- CPython's `contextvars`, which uses a HAMT internally so that copying a context is cheap

## Why bother: what sharing buys you

### Cheap snapshots and undo

Retaining an old root is a cheap snapshot, but keeps its reachable nodes alive. An editor's undo stack is just a list of previous document values. A game can keep the last 60 game states for rewind with memory proportional to what changed.

### O(1) change detection

If two references point to the same object, nothing inside changed. React and Redux depend on this: `React.memo` compares each prop with `Object.is`, and Redux's `useSelector` compares results by reference, which is only correct if updates create new objects rather than mutating old ones. Many persistent APIs reuse identity for no-op updates, but that behavior is API-dependent; different references need not mean different contents.

### Safe sharing across threads

Deeply immutable data can avoid locks for its contents after safe publication and while its lifetime is guaranteed; mutable elements or reference-management protocols still need care. A Clojure atom holds a persistent value: a writer builds a new version and swaps a single pointer with compare-and-set, while readers keep using whatever version they grabbed.

## Where it gets hard

### Constant factors

A persistent vector lookup is several dependent pointer loads; an array lookup is one. Each update allocates fresh nodes, which means garbage collection pressure. For a tight numeric loop over a large array, a mutable array is typically much faster. Persistent collections win when you actually need old versions or sharing, not by default.

### Amortisation breaks under persistence

The classic functional queue keeps two lists: `front` for popping and `back` for pushing (newest first). When `front` runs out, reverse `back` into a new `front`:

```python
def push(q, x):
    front, back = q
    return front, (x, back)

def pop(q):
    front, back = q
    if front is None:
        while back is not None:
            x, back = back
            front = (x, front)
    if front is None:
        raise IndexError("empty queue")
    x, rest = front
    return x, (rest, back)
```

Each list is a nested (head, tail) tuple ending in None, as above; the empty queue is (None, None). Both prepend and tail access are O(1).

Used normally, each element is reversed once, so the costs average out to O(1) per operation: a fixed cost however long the queue. That's an **amortised** bound (an **amortised cost**): occasional expensive reverses are paid for by many cheap pushes.

```formula
T_total ≤ 2 × m
T_avg = T_total / m ≤ 2
where
T_total: the total number of basic steps (one per push, one per element moved by a reverse, one per pop) for a whole sequence of operations on one queue that is always used in its latest version
m: the number of push and pop operations in the sequence
T_avg: the average (amortised) cost per operation
≤: less than or equal to
In words: each element is pushed once, moved by a reverse at most once and popped once, so the whole sequence costs at most about two steps per operation, however unevenly those steps fall.
```

For example, 1,000 pushes followed by 1,000 pops cost 1,000 push steps, one 1,000-step reverse and 1,000 pop steps: 3,000 steps for m = 2,000 operations, an average of 1.5.

Persistence breaks the argument. Take a version `q` whose `front` is empty and whose `back` holds n items. If you call `pop(q)` a thousand times (on the *same* old version, which persistence explicitly allows), each call does the full O(n) reverse. The "savings" from cheap pushes were spent once, but the expensive step is replayed every time.

```formula
T_replay = k × n
T_replay = 1000 × 1000 = 1000000
where
T_replay: the total reversal steps when pop is called k times on the same old version
k: the number of pops on that one version
n: the number of items in its back list
In words: every pop on the old version redoes the full reverse, so the cost is k times n rather than n once.
```

With n = 1,000 items and k = 1,000 pops, that's a million copies instead of a thousand.

Chris Okasaki's fix, in *Purely Functional Data Structures*, is to combine persistence with **laziness**: arrange lazy memoized work so branches share one thunk (suspended computation) created before they diverge. Creating a fresh thunk in each pop would still repeat the reversal. Appropriate invariants recover amortised bounds; incremental rotation and scheduling are additionally needed for worst-case O(1).

> [!warning] Rule of thumb
> If a persistent structure's docs say "amortised", check whether that bound holds when old versions are reused. Okasaki-style structures are designed for it; a naive port of a mutable algorithm usually isn't.

### Bulk builds and transients

Building a 100,000-element vector by 100,000 persistent appends creates 100,000 intermediate versions that nobody will ever look at. Libraries offer a controlled escape hatch:

- **Clojure transients**: `(persistent! (reduce conj! (transient []) xs))` uses an isolated transient, then returns a persistent value in O(1). Always capture the returned transient from each update and stop using it after persistent!.
- **Immutable.js** `withMutations`: batch updates on a temporary mutable copy.
- **Immer** (JavaScript): write ordinary mutating code against a draft; it produces a new immutable object that shares every untouched part with the original.

All three rely on the same insight: mutation is safe as long as no one else holds a reference to the thing being mutated.

### Python's options

In CPython, appending to a nonempty tuple with t + (x,) copies its references in O(n), where n is the tuple's length, while the elements themselves remain shared. This preserves the old tuple and is persistent in the semantic sense, but lacks an efficient tree-based update path. For real persistent collections, use a library such as `pyrsistent` (`pvector`, `pmap`, `pset`), or accept copying when the data is small.

## Key takeaways
- Persistent structures keep old versions valid; structural sharing is a technique for doing so efficiently.
- Cons lists share tails: prepend is O(1), but append and indexed update copy the prefix.
- Trees use path copying: copy the root-to-change path, O(log n) nodes, and reuse every other subtree.
- 32-way tries (vectors) and HAMTs (maps, sets) keep depth around 4 for a million items, making updates and lookups "effectively constant".
- Sharing gives cheap snapshot roots and useful identity checks; safe publication, deep immutability and lifetime management still govern concurrent reads.
- Costs are pointer chasing, allocation and GC; amortised bounds can break when old versions are reused, which Okasaki fixes with laziness.
- Transients, `withMutations` and Immer allow local mutation for bulk work, then freeze the result.

## Further reading
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Hash array mapped trie — Wikipedia](https://en.wikipedia.org/wiki/Hash_array_mapped_trie)
- [Purely Functional Data Structures (thesis) — Chris Okasaki](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf)
- [Data Structures — Clojure reference](https://clojure.org/reference/data_structures)
- [Transient Data Structures — Clojure reference](https://clojure.org/reference/transients)
- [Git Internals: Git Objects — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [pyrsistent — GitHub](https://github.com/tobgu/pyrsistent)
- [Primary verification source 3](https://github.com/clojure/clojure/blob/master/src/jvm/clojure/lang/PersistentVector.java)
- [Primary verification source 4](https://www.erlang.org/doc/system/maps.html)
- [Primary verification source 5](https://hackage.haskell.org/package/containers/docs/Data-Map-Lazy.html)
- [Primary verification source 6](https://peps.python.org/pep-0567/)
- [Primary verification source 7](https://docs.scala-lang.org/overviews/collections-2.13/concrete-immutable-collection-classes.html)
- [Primary verification source 8](https://immerjs.github.io/immer/produce/)
- [Primary verification source 9](https://react-redux.js.org/api/hooks#equality-comparisons-and-updates)
- [Primary verification source 10](https://github.com/python/cpython/blob/main/Objects/tupleobject.c)
