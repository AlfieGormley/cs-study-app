---
id: lin-list-doubly-sentinel
title: Doubly linked lists and sentinels
level: intermediate
minutes: 3
sourceLesson: lin-linked-lists
summary: Unlinking must update both neighbours.
---

A singly linked list has no backwards link. A doubly linked list adds a predecessor reference so both neighbours can be reconnected when a known node is removed. Constant-time claims count pointer operations on valid handles, not allocator or value-destruction time.

## Doubly linked lists

Add a `prev` pointer to every node and you can walk in both directions, and delete any node in O(1) given only that node:

```
None<-[3]<=>[8]<=>[5]->None
```

```python
def unlink(node):
    # Repair the forward neighbour link.
    node.prev.next = node.next
    # Repair the backward neighbour link.
    node.next.prev = node.prev
```

That code crashes when `node` is the head (`node.prev` is `None`) or the tail. Handling those cases with `if` statements everywhere is tedious and error-prone. Which brings us to sentinels.

## Sentinel nodes

A **sentinel** (or dummy) node is a node that holds no data and is always present. With a circular doubly linked sentinel, every real node has neighbours on both sides even when there are no other data nodes. The data sequence can be empty while the sentinel remains.

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
        # An unattached node points to
        # itself.
        self.prev = self.next = self

class DList:
    def __init__(self):
        self.s = DNode()   # sentinel

    def insert_after(self, p, val):
        n = DNode(val)
        # Link the newcomer to both
        # neighbours.
        n.prev, n.next = p, p.next
        # Redirect the old successor
        # backwards.
        p.next.prev = n
        # Publish the new forward
        # connection.
        p.next = n
        return n

    def push_front(self, val):
        s = self.s
        return self.insert_after(s, val)

    def push_back(self, val):
        last = self.s.prev
        return self.insert_after(last, val)

    def remove(self, n):
        # Bypass the node when walking
        # forwards.
        n.prev.next = n.next
        # Bypass it when walking backwards.
        n.next.prev = n.prev
```

For valid handles belonging to this list, insertion and removal use a constant number of pointer updates. Do not remove the sentinel or remove a node twice. Allocation and value destruction are outside this pointer-operation model. There is no special case for an empty list, the first node or the last node. The Linux kernel's `struct list_head` uses exactly this design, with intrusive link fields embedded in containing objects.

> [!tip] The cost of a sentinel
> One extra node of memory per list. For a list with millions of entries that's nothing; for millions of tiny lists it can add up.

## Key takeaways
- Unlinking must update both neighbours.
- A circular sentinel makes every valid data-node removal use the same pointer updates.

## Further reading
- [Doubly linked list — Wikipedia](https://en.wikipedia.org/wiki/Doubly_linked_list)
- [Linux kernel API: list management](https://www.kernel.org/doc/html/latest/core-api/kernel-api.html)
- [Linux — linked-list API and circular sentinels](https://docs.kernel.org/core-api/list.html)
