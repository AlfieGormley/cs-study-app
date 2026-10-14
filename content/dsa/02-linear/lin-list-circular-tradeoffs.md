---
id: lin-list-circular-tradeoffs
title: Circular lists and production trade-offs
level: intermediate
minutes: 5
sourceLesson: lin-linked-lists
summary: A tail-only circular list exposes its head through the tail link.
---

The preceding units showed why knowing the node changes a list operation’s cost. Here n is the number of data elements. Circular organisation changes termination rules; practical layout and stable-handle requirements decide whether pointer-based storage is worthwhile.

## Circular lists

In a **circular** list the last node points back to the first instead of to `None`. Circular singly linked lists are handy for round-robin scheduling: keep a pointer to the current node and advance it forever.

A neat trick: keep only a **tail pointer**. Then `tail.next` is the head, so you get O(1) access to both ends from one pointer.

The danger with circular lists is the loop condition. `while cur:` never ends; you must stop when you return to your starting node.

## Cost summary

For a sequence of n elements, keeping both head and tail handles for the doubly linked representation and using constant-time value/allocation operations:

| Operation | Array | Singly | Doubly |
|---|---|---|---|
| Access i-th | O(1) | O(n) | O(n) |
| Insert/delete at front | O(n) | O(1) | O(1) |
| Insert/delete at back | O(1) amortised | See below | O(1) |
| Delete given node | O(n) | O(n) | O(1) |
| Insert after given node | O(n) | O(1) | O(1) |

For a singly linked list, inserting at the back is O(1) if you keep a tail pointer, but deleting the last node is O(n), because you have to walk to its predecessor.

## The hidden costs

Big-O makes linked lists look great for insertion-heavy work. Real hardware is less kind.

- **Memory overhead.** Every node carries one or two pointers plus allocator bookkeeping. A Java `LinkedList` node is an object with three references (item, next, prev); for small elements, the overhead dwarfs the data. A Python node object costs tens of bytes before you even count the value.
- **Cache misses.** Nodes are scattered around the heap. Walking a list is a chain of dependent loads: the CPU can't fetch node 5 until node 4 tells it where node 5 is. Arrays stream through cache with prefetching.
- **Allocation.** Separately allocated nodes add allocation/reclamation work; pools and intrusive lists can avoid a per-insertion allocation.
- **Finding the spot is O(n) anyway** (for n elements). "Insert in the middle is O(1)" assumes you already hold the node. If you have to search for the position first, that search is O(n), and on an array it is a fast linear scan.

> [!example] Why locality can outweigh shifting
> A vector can beat a linked list when both first perform a linear search for the insertion point: contiguous scanning and shifting may outweigh the cost of moving elements. Actual performance requires measurement.

> [!note] Evidence gap
> A specific historical benchmark result is omitted because its exact dataset, implementation and measurements have not been independently reproduced or sourced here.

## When linked lists actually win

Linked lists earn their place when you **already hold a reference** to the node you want to change, or when you need properties arrays can't give:

1. **O(1) removal from the middle via a handle.** An LRU cache pairs a hash map (key to node) with a doubly linked list. On every hit it unlinks the node and moves it to the front in O(1). This is how Python's `OrderedDict` and Java's `LinkedHashMap` keep order.
2. **Stable references.** Inserting into or removing from a `std::list` never invalidates iterators to other elements. A vector's reallocation invalidates all of them.
3. **Splicing.** Relinking a run with known boundaries takes a few pointer changes, but maintaining container metadata can add work. C++ std::list range-splice between different lists is linear in the range length; whole-list and single-element splice are constant-time under their allocator preconditions.
4. **No reallocation spikes.** A linked queue never has to copy everything to grow, but allocation, reclamation and synchronization still need bounded-latency designs for hard real-time use.
5. **Intrusive lists.** In kernels and game engines, the `next`/`prev` pointers live inside the object itself, so membership needs no separate node allocation; simultaneous membership in several lists requires a separate link pair for each list.
6. **Immutable sharing.** In functional languages (Haskell, Lisp, Scala's `List`), prepending to a list creates one new node that points at the old list. Both versions remain valid and share the tail.

Many practical structures are hybrids. CPython's `collections.deque` is a doubly linked list of **blocks**, each holding 64 items. It keeps O(1) operations at both ends while getting most of an array's cache-friendliness.

## Key takeaways
- A tail-only circular list exposes its head through the tail link.
- Known handles, stable references and shared immutable tails are reasons to accept pointer overhead.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [LinkedList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html)
- [Linux kernel API: list management](https://www.kernel.org/doc/html/latest/core-api/kernel-api.html)
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
