---
id: lin-list-rewire-singly
title: Rewiring a singly linked list
level: intermediate
minutes: 2
sourceLesson: lin-linked-lists
summary: Preserve the old successor before replacing a link.
---

A singly linked node has a value and a next reference. Use the Node class from the preceding unit. The operations below assume a finite, acyclic list and valid node handles; deletion also needs a successor to remove. Here n is the number of nodes.

### Insertion

Inserting at the head is O(1), and so is inserting after a node you already hold:

```python
# push to front
head = Node(1, head)

# insert x after node p
# Keep the old suffix in the new node.
p.next = Node(x, p.next)
```

```
before:  p -> [8] -> [5]
after:   p -> [x] -> [8] -> [5]
```

Order matters. Create the new node pointing at `p.next` *first*, then point `p` at it. Do it the other way round and you lose the rest of the list.

Inserting at the tail of an n-node list is O(n), because you must walk to the last node, unless you also keep a `tail` pointer, in which case it is O(1).

### Deletion

To remove a node you need the node **before** it, so you can skip over it:

```python
# remove the node after p
# Bypass one existing successor node.
p.next = p.next.next
```

This is the singly linked list's big weakness. Given only a pointer to a non-head node, you cannot unlink that node in O(1), because you cannot reach its predecessor without walking from the head. Copying the successor’s value into it and skipping the successor is not the same operation: it changes what existing handles observe and fails at the tail. Removing the head is a special case (`head = head.next`), and that special-casing is a common source of bugs.

## Key takeaways
- Preserve the old successor before replacing a link.
- Deleting a real node requires its predecessor; copying a value is a different operation.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
