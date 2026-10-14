---
id: lin-list-reversal-pattern
title: Reverse links while preserving the suffix
level: intermediate
minutes: 3
sourceLesson: lin-list-techniques
summary: Save the remaining suffix before flipping a next pointer.
---

Most linked-list problems, in interviews and in real code, reduce to a few patterns. Learn these four and you can assemble the rest:

1. **Reversal**: turn every arrow around in one pass.
2. **Fast and slow pointers**: two pointers moving at different speeds.
3. **Merging**: weave two sorted lists together.
4. **Dummy heads**: a throwaway node in front so the real head is never a special case.

For a list of n nodes, the iterative patterns below use linear time, O(n), and **O(1) extra space** (a fixed handful of pointer variables, however long the list); recursive reversal is an explicit exception. Unless detecting a cycle, assume finite acyclic lists. That last part is the point: anyone can solve these problems by copying the list into an array first, but then you've spent O(n) memory.

Throughout, we use:

```python
class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next
```

## Reversal

Reversing a singly linked list in place means making every `next` point backwards. You need three pointers: the node you're working on (`cur`), the part already reversed (`prev`), and the rest of the list (`nxt`), which you must save before you break the link to it.

```python
def reverse(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next   # save the rest
        cur.next = prev  # flip the arrow
        prev = cur       # grow reversed
        cur = nxt        # move on
    return prev          # new head
```

The following is an execution-state trace of the Python function on the three-node chain:

```
start   prev=None  cur=1   1->2->3
iter 1  None<-1    prev=1  cur=2
iter 2  None<-1<-2 prev=2  cur=3
iter 3  None<-1<-2<-3
        prev=3     cur=None
return 3:  3->2->1
```

Each of the n nodes is visited once: O(n) time, O(1) space.

### Recursive reversal

```python
def reverse_rec(head):
    if head is None or head.next is None:
        return head
    # Reverse the suffix before linking
    # back.
    new_head = reverse_rec(head.next)
    head.next.next = head  # flip
    # The old head becomes the new tail.
    head.next = None
    return new_head
```

It's elegant, but on an n-node list it uses **O(n) stack space**, one frame per node. A conventional CPython build commonly starts with a recursion limit of 1,000; inspect `sys.getrecursionlimit()` rather than assuming an unchanged configuration. Under that setting a 10,000-node recursive reversal raises `RecursionError`. Prefer the loop.

## Key takeaways
- Save the remaining suffix before flipping a next pointer.
- An iterative reversal keeps a fixed pointer set; recursion retains one frame per node.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [sys.setrecursionlimit — Python docs](https://docs.python.org/3/library/sys.html)
