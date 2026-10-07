---
id: fp-persistent-data
title: Persistent data structures
level: advanced
minutes: 14
summary: How immutable lists, trees, maps and vectors make cheap "modified copies" by sharing structure, the 32-way tries behind Clojure, Scala and Immutable.js, and the traps where persistence breaks amortised bounds.
---

Immutability has an obvious cost. If you can never change a list in place, then "add one element" seems to mean "copy the whole list and add one element". Do that in a loop over a million items and you've written an O(n²) algorithm.

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

The costs show up at the other end:

| Operation | Cost | Why |
|---|---|---|
| Prepend | O(1) | new head, shared tail |
| Head / tail | O(1) | follow one pointer |
| Append | O(n) | copy every cell |
| Index i | O(i) | walk i pointers |
| Update at i | O(i) | copy cells 0..i |

Appending must copy every cell, because the last cell's pointer has to change and every cell before it points (indirectly) at that one. For this immutable linked-list path-copying scheme, copy the prefix leading to the change; persistence in general has other implementation techniques.

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

For a **balanced** tree of n keys, the path has about log₂ n nodes. With a million keys that's about 20 new nodes per insert, instead of a million. Both versions remain fully usable, and the extra memory is O(log n) per update.

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

Ignoring tail optimization and partially filled roots, the number of array levels is ceil(log₃₂ n):

| Elements | Levels |
|---|---|
| 32 | 1 |
| 1,024 | 2 |
| 32,768 | 3 |
| ~1 million | 4 |
| ~1 billion | 6 |

Six hops for a billion elements is why people call these operations "effectively constant". They are still O(log n), but the base is 32.

Updating index i uses path copying: copy each node on the path (each a 32-slot array) and change one slot. For a million-element vector that's 4 arrays of 32 pointers, about 1 KB at 8 bytes a pointer, versus 8 MB to copy the whole backing array.

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

Retaining an old root is a cheap snapshot, but keeps its reachable nodes alive. An editor's undo stack is just a list of previous document values. A game can keep the last 60 frames of state for rewind with memory proportional to what changed.

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

Used normally, each element is reversed once, so the costs average out to O(1) per operation. That's an **amortised** bound: occasional expensive reverses are paid for by many cheap pushes.

Persistence breaks the argument. Take a version `q` whose `front` is empty and whose `back` holds n items. If you call `pop(q)` a thousand times (on the *same* old version, which persistence explicitly allows), each call does the full O(n) reverse. The "savings" from cheap pushes were spent once, but the expensive step is replayed every time.

Chris Okasaki's fix, in *Purely Functional Data Structures*, is to combine persistence with **laziness**: arrange lazy memoized work so branches share a suspension created before they diverge. Creating a fresh thunk in each pop would still repeat the reversal. Appropriate invariants recover amortised bounds; incremental rotation and scheduling are additionally needed for worst-case O(1).

> [!warning] Rule of thumb
> If a persistent structure's docs say "amortised", check whether that bound holds when old versions are reused. Okasaki-style structures are designed for it; a naive port of a mutable algorithm usually isn't.

### Bulk builds and transients

Building a 100,000-element vector by 100,000 persistent appends creates 100,000 intermediate versions that nobody will ever look at. Libraries offer a controlled escape hatch:

- **Clojure transients**: `(persistent! (reduce conj! (transient []) xs))` uses an isolated transient, then returns a persistent value in O(1). Always capture the returned transient from each update and stop using it after persistent!.
- **Immutable.js** `withMutations`: batch updates on a temporary mutable copy.
- **Immer** (JavaScript): write ordinary mutating code against a draft; it produces a new immutable object that shares every untouched part with the original.

All three rely on the same insight: mutation is safe as long as no one else holds a reference to the thing being mutated.

### Python's options

In CPython, appending to a nonempty tuple with t + (x,) copies its references in O(n), while the elements themselves remain shared. This preserves the old tuple and is persistent in the semantic sense, but lacks an efficient tree-based update path. For real persistent collections, use a library such as `pyrsistent` (`pvector`, `pmap`, `pset`), or accept copying when the data is small.

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
