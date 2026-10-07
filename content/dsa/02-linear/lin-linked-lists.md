---
id: lin-linked-lists
title: Linked lists
level: intermediate
minutes: 12
summary: Singly, doubly and circular linked lists, how sentinel nodes remove edge cases, the real costs of insertion and deletion, and the specific situations where linked lists beat arrays.
---

An array keeps its elements side by side. A **linked list** gives that up: each element lives in its own **node**, anywhere in memory, and each node holds a pointer to the next one.

```
head
 |
 v
[3|*]--->[8|*]--->[5|*]--->None
 val next
```

That one change flips the trade-offs:

- You can no longer jump to element `i`; you must walk there. Access becomes **O(n)**.
- But if you already hold a node, you can insert or remove next to it by rewiring a couple of pointers, with no shifting. That's **O(1)**.

Linked lists are a staple of interviews and textbooks. In production code they are less common than you might expect, and knowing *why* is part of mastering them.

## Singly linked lists

Each node has a value and a `next` pointer. The list itself is just a reference to the first node, the **head**. The last node's `next` is `None`.

```python
class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

# build 3 -> 8 -> 5
head = Node(3, Node(8, Node(5)))
```

### Traversal and search

```python
def find(head, target):
    cur = head
    while cur:
        if cur.val == target:
            return cur
        cur = cur.next
    return None
```

Getting the k-th element, or searching for a value, is O(n): you follow k pointers.

### Insertion

Inserting at the head is O(1), and so is inserting after a node you already hold:

```python
# push to front
head = Node(1, head)

# insert x after node p
p.next = Node(x, p.next)
```

```
before:  p -> [8] -> [5]
after:   p -> [x] -> [8] -> [5]
```

Order matters. Create the new node pointing at `p.next` *first*, then point `p` at it. Do it the other way round and you lose the rest of the list.

Inserting at the tail is O(n) unless you also keep a `tail` pointer, in which case it is O(1).

### Deletion

To remove a node you need the node **before** it, so you can skip over it:

```python
# remove the node after p
p.next = p.next.next
```

This is the singly linked list's big weakness. Given only a pointer to a node, you can't unlink it in O(1), because you can't reach its predecessor without walking from the head. Removing the head is a special case (`head = head.next`), and that special-casing is a common source of bugs.

## Doubly linked lists

Add a `prev` pointer to every node and you can walk in both directions, and delete any node in O(1) given only that node:

```
None<-[3]<=>[8]<=>[5]->None
```

```python
def unlink(node):
    node.prev.next = node.next
    node.next.prev = node.prev
```

That code crashes when `node` is the head (`node.prev` is `None`) or the tail. Handling those cases with `if` statements everywhere is tedious and error-prone. Which brings us to sentinels.

## Sentinel nodes

A **sentinel** (or dummy) node is a node that holds no data and is always present. With a sentinel, the list is never truly empty and every real node always has a real neighbour on both sides.

The neatest version is a **circular doubly linked list with one sentinel**: the sentinel's `next` is the first element and its `prev` is the last.

```
   +--------------------------+
   v                          |
[sent] <=> [3] <=> [8] <=> [5]
   |                          ^
   +--------------------------+

empty list: sent.next = sent.prev = sent
```

```python
class DNode:
    def __init__(self, val=None):
        self.val = val
        self.prev = self.next = self

class DList:
    def __init__(self):
        self.s = DNode()   # sentinel

    def insert_after(self, p, val):
        n = DNode(val)
        n.prev, n.next = p, p.next
        p.next.prev = n
        p.next = n
        return n

    def push_front(self, val):
        s = self.s
        return self.insert_after(s, val)

    def push_back(self, val):
        last = self.s.prev
        return self.insert_after(last, val)

    def remove(self, n):
        n.prev.next = n.next
        n.next.prev = n.prev
```

For valid handles belonging to this list, insertion and removal use a constant number of pointer updates. Do not remove the sentinel or remove a node twice. Allocation and value destruction are outside this pointer-operation model. There is no special case for an empty list, the first node or the last node. The Linux kernel's `struct list_head` uses exactly this design, with intrusive link fields embedded in containing objects.

> [!tip] The cost of a sentinel
> One extra node of memory per list. For a list with millions of entries that's nothing; for millions of tiny lists it can add up.

## Circular lists

In a **circular** list the last node points back to the first instead of to `None`. Circular singly linked lists are handy for round-robin scheduling: keep a pointer to the current node and advance it forever.

A neat trick: keep only a **tail** pointer. Then `tail.next` is the head, so you get O(1) access to both ends from one pointer.

The danger with circular lists is the loop condition. `while cur:` never ends; you must stop when you return to your starting node.

## Cost summary

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
- **Finding the spot is O(n) anyway.** "Insert in the middle is O(1)" assumes you already hold the node. If you have to search for the position first, that search is O(n), and on an array it is a fast linear scan.

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
- A linked list trades O(1) indexing for O(1) insertion and deletion next to a node you already hold.
- Singly linked lists can't delete a node without its predecessor; doubly linked lists can, in O(1).
- A sentinel node removes the empty, head and tail special cases; a circular list with one sentinel is the cleanest design.
- Pointer overhead, allocation and cache misses mean arrays usually win in practice, even for insertion-heavy work.
- Use linked lists when you hold node handles (LRU caches), need stable references, splice, or share immutable tails.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [Doubly linked list — Wikipedia](https://en.wikipedia.org/wiki/Doubly_linked_list)
- [LinkedList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html)
- [Linux kernel API: list management](https://www.kernel.org/doc/html/latest/core-api/kernel-api.html)
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
- [XOR linked list — Wikipedia](https://en.wikipedia.org/wiki/XOR_linked_list)
