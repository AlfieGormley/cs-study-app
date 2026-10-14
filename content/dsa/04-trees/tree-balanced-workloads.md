---
id: tree-balanced-workloads
title: Choosing balanced trees for real workloads
level: intermediate
minutes: 5
sourceLesson: tree-balanced
summary: AVL has a tighter worst-case height bound, but speed needs measurement.
---

Start with the distinct-key BST ordering from the previous units. A rotation must keep the same sorted in-order sequence while changing local links. Here n counts stored keys and h measures real-node height in edges; empty subtrees have height minus one unless a NIL-path convention is explicitly given. Height bounds assume constant-cost key comparisons, rather than measuring application latency.

## AVL versus red-black

Side by side, the two height bounds for n keys are:

```formula
h_AVL ≈ 1.44 log_2(n)
h_RB ≤ 2 log_2(n + 1)
h_AVL ≈ 1.44 × 19.93 ≈ 28.7
h_RB ≤ 2 × 19.93 ≈ 39.9
where
h_AVL: the greatest possible height of an AVL tree, in edges (an approximation for large n)
h_RB: the greatest possible height of a red-black tree, in edges
n: the number of keys stored; the last two lines use n = 10^6, for which log_2(n) ≈ 19.93
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≈: approximately equal to
≤: is at most
In words: the red-black worst-case height bound is about 40 % higher than the AVL one for the same number of keys; both are logarithmic in n.
```

(The exact AVL worst case for a million keys is 27, from the recurrence above.)

| | AVL | Red-black |
|---|---|---|
| Max height | Approx. 1.44 times the base-2 logarithm | Twice the base-2 log of one more key |
| Lookup height bound | Tighter | Looser |
| Rotations/insert | At most one repair | At most two |
| Rotations/delete | O(log n) | At most three |
| Extra data | Height or balance factor | 1 colour bit |

Search and single-key updates are O(log n) for n keys, with constant-cost comparisons; traversing all entries is O(n). Practical tradeoffs:

- AVL offers a tighter worst-case height bound; actual read performance needs measurement.
- **Write-heavy** or general-purpose libraries usually choose red-black: fewer rotations on delete, and a colour bit can be hidden in the low bit of an aligned pointer, as the Linux kernel does.

## Where they are used

- **Java `TreeMap` and `TreeSet`**: red-black trees, giving logarithmic get, put, floorKey and ceilingKey operations; full sorted iteration over n entries takes O(n).
- **Java `HashMap`**: since Java 8, when a single bucket grows past 8 colliding entries (in a table of at least 64 buckets), it is converted into a small red-black tree, Comparable keys can use ordering to obtain logarithmic bin searches. Equal-hash keys without usable comparison ordering can still require linear search within a tree bin.
- **C++ `std::map` and `std::set`**: red-black trees in the major standard libraries (libstdc++, libc++, MSVC). The standard requires logarithmic key lookup and key-based updates for n elements, with other operation-specific bounds; erasing through a known iterator is amortised constant time. Insertion preserves iterators, without requiring a specific representation.
- **Linux kernel**: a generic intrusive rbtree (`lib/rbtree.c`) used widely. The **Completely Fair Scheduler** kept runnable tasks in a red-black tree ordered by `vruntime` (virtual runtime) and ran the leftmost task, caching a pointer to it so picking the next task is O(1). Linux began transitioning fair scheduling toward EEVDF in version 6.6; its implementation uses an augmented red-black tree. `epoll` also stores its watched file descriptors in one.

> [!example] Why CFS wanted a tree, not a binary heap
> A binary heap gives the minimum just as fast. But the scheduler also removes arbitrary tasks (one blocks on I/O, one is killed) and re-inserts them with new keys. With an intrusive tree, each task embeds its own tree node, so removing a given task from n runnable tasks is O(log n) with no search. A binary heap would need an extra position index to find an arbitrary entry, and it cannot cheaply answer "which task comes next after this one?".

### Other balanced structures, briefly

- **B-trees and B+ trees** use the same idea with hundreds of keys per node, matching disk pages. Many relational database indexes use them; hash, bitmap and other index types also exist (covered in System Design: databases).
- **Skip lists** give expected O(log n) search over n keys with randomised towers of linked lists; Redis sorted sets can use a skip list plus dictionary or a compact encoding.
- **Treaps** and **splay trees** balance with randomness or by moving accessed nodes to the root.
- Python has no built-in balanced tree. `sortedcontainers` uses a list of sorted lists, which offers different locality and update tradeoffs from pointer-based trees.

> [!note] Evidence gap
> Universal AVL-versus-red-black lookup wins and sortedcontainers performance wins are omitted because no matching workload, implementation and reproducible benchmark were supplied.

## Key takeaways
- AVL has a tighter worst-case height bound, but speed needs measurement.
- Conventional red-black deletion uses a bounded number of rotations.
- Library and kernel uses must be distinguished from interface requirements.

## Further reading
- [Left-leaning Red-Black Trees — Robert Sedgewick (PDF)](https://sedgewick.io/wp-content/themes/sedgewick/papers/2008LLRB.pdf)
- [Red-black Trees (rbtree) in Linux — kernel docs](https://docs.kernel.org/core-api/rbtree.html)
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [TreeMap (Java SE 25) — Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html)
- [HashMap implementation — OpenJDK](https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/util/HashMap.java)
- [Associative container requirements — C++ draft](https://eel.is/c++draft/associative.reqmts)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
