---
id: lin-list-node-traversal
title: Nodes, traversal and positional search
level: intermediate
minutes: 3
sourceLesson: lin-linked-lists
summary: A node stores a value and a link rather than a positional address shortcut.
---

An array keeps its elements side by side. A **linked list** gives that up: each element lives in its own **node**, anywhere in memory, and each node holds a pointer to the next one.

```
head
 |
 v
[3|*]--->[8|*]--->[5|*]--->None
 val next
```

That one change flips the trade-offs. For a list of n elements:

- You can no longer jump to element `i`; you must walk there. Access becomes **O(n)**.
- But if you already hold a node, you can insert or remove next to it by rewiring a couple of pointers, with no shifting. That's **O(1)**.

Linked lists are a staple of interviews and textbooks. In production code they are less common than you might expect, and knowing *why* is part of mastering them.

## Singly linked lists

Each node has a value and a `next` pointer. The list itself is just a reference to the first node, the **head node** (or just the head). The last node's `next` is `None`.

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
        # Follow the link, not a numeric
        # index.
        cur = cur.next
    return None
```

Getting the k-th element means following k pointers, so it costs O(k + 1), including the final value read; this is O(n) in the worst case for a list of n nodes. Searching for a value is O(n) too: you may have to look at every node.

### Avoid repeating positional traversal

Calling an indexed accessor repeatedly does not retain the previous traversal position. A Java LinkedList lookup starts from whichever end is nearer the requested position. That is helpful for one lookup but still repeats walking when an index-based loop visits every element.

For one hundred thousand nodes, an index loop sums billions of dependent pointer hops. An iterator instead remembers the current node and follows one link per next element, giving a single linear traversal. When you need repeated arbitrary positional lookup, a dynamic array usually matches the access pattern better.

This explains an important distinction: a linked list can support a constant-time update next to a handle you already hold, but locating that handle is a different operation. The next unit examines those updates, including the order in which successor links must change.

## Key takeaways
- A node stores a value and a link rather than a positional address shortcut.
- Repeated indexed access to a linked list can repeat the traversal.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [LinkedList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html)
