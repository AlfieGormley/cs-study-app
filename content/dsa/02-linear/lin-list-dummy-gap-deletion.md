---
id: lin-list-dummy-gap-deletion
title: Dummy heads and fixed-gap deletion
level: intermediate
minutes: 3
sourceLesson: lin-list-techniques
summary: A dummy supplies a predecessor even for the real head.
---

Use the Node class from the reversal unit and assume a finite, acyclic list. Here n is the requested one-based distance from the end, rather than the list length. A temporary dummy node supplies a stable predecessor even when the target is the real head.

## Dummy heads

Many list operations treat the first node specially: deleting it changes `head`, and building a new list has no node to attach the first element to. A **dummy head** (a sentinel placed before the real head) removes the special case. Build or modify the list after the dummy, then return `dummy.next`.

### Removing the n-th node from the end

Use two pointers with a gap of n between them. When the front one hits the end, the back one is just before the target.

```python
def remove_nth_from_end(head, n):
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be >= 1")
    # Give the real head a predecessor.
    dummy = Node(0, head)
    front = back = dummy
    # Keep back just before the target.
    for _ in range(n + 1):
        if front is None:
            raise ValueError("n too large")
        front = front.next
    while front:
        front = front.next
        back = back.next
    # Remove the target after validation.
    back.next = back.next.next
    return dummy.next
```

Without the dummy, removing the *first* node (when n equals the length) needs its own branch. With it, `back` simply stays at the dummy and the general code works.

### Trace the boundary cases

On the five-node chain with values one through five, requesting the last node leaves the back pointer at node four when front runs off the chain. Requesting the fifth node from the end keeps back at the dummy; bypassing its successor removes the real head with the same statement.

The extra initial step is intentional: back must end before the target, not on it. Advancing beyond the available chain raises the explicit error before any link is changed. An empty list has no valid positive removal distance. A zero or negative distance is rejected, rather than silently removing an unrelated node.

Python treats bool as an int subclass, so the shown isinstance check accepts True as distance one. Callers that must reject Boolean arguments need a stricter validation contract. This teaching example otherwise leaves all non-target node identities intact.

## Key takeaways
- A dummy supplies a predecessor even for the real head.
- Validate the requested position before bypassing a target.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
