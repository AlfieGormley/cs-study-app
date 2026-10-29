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

> [!analogy] Real-world analogy: A treasure hunt
> In a treasure hunt each clue tells you where the next clue is hidden. To reach clue 5 you must find clues 1 to 4 first, but slipping a new clue in after clue 3 only means rewriting clue 3 to point at it.
>
> **How it maps:** Each clue is a node, the directions on it are the `next` pointer, and the first clue's location is `head`. Following clues one by one is traversal, so reaching position k costs k hops, while inserting after a clue you are holding is a constant-time rewire.
>
> **Where it stops:** Following a pointer takes nanoseconds, not a walk across a park, although each hop can still miss the cache. A real list also needs a definite end, where the last node's `next` is `None`, and unlike paper clues, nodes are never consumed by reading them.

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

For one hundred thousand nodes, an index loop that calls `get(i)` for every position re-walks from an end each time, adding up to billions of dependent pointer hops: quadratic total work. An iterator instead remembers the current node and follows one link per next element, giving a single linear traversal. When you need repeated arbitrary positional lookup, a dynamic array usually matches the access pattern better.

This explains an important distinction: a linked list can support a constant-time update next to a handle you already hold, but locating that handle is a different operation. The next unit examines those updates, including the order in which successor links must change.

## Key takeaways
- A node stores a value and a link rather than a positional address shortcut.
- Repeated indexed access to a linked list can repeat the traversal.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [LinkedList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html)
