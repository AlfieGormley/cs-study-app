---
id: lin-list-middle-cycle-detection
title: Fast and slow pointers: middle and cycles
level: intermediate
minutes: 3
sourceLesson: lin-list-techniques
summary: The loop condition determines which even-length middle is returned.
---

Use the singly linked Node class from the reversal unit. In an acyclic list of n nodes, one- and two-link moves find a middle without counting the length first. On a cyclic list they instead reveal whether the same node is reached at the same time.

## Fast and slow pointers

Move one pointer (`slow`) one step at a time and another (`fast`) two steps. The gap between them grows by one each step. That simple fact answers several questions in one pass.

### Finding the middle

When `fast` reaches the end, `slow` has gone half as far.

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        # Two links for every one slow
        # link.
        fast = fast.next.next
    return slow
```

The following execution-state trace records the Python pointer values.

```
1 -> 2 -> 3 -> 4 -> 5
step 0: slow=1 fast=1
step 1: slow=2 fast=3
step 2: slow=3 fast=5  (stop)
middle = 3
```

For an even-length list such as `1..6`, this returns **4**, the second of the two middle nodes. If you need the first middle (useful for splitting a list in half for merge sort), use `while fast and fast.next and fast.next.next` to handle empty input too.

### Floyd's cycle detection

A bug or a malicious input can make a list loop back on itself. Walking it with `while cur:` then never ends. How do you detect a cycle?

The obvious answer is a set of visited nodes: for a list of n nodes that is O(n) time but **O(n) memory**. **Floyd's algorithm** (the "tortoise and hare") does it in O(1) memory.

If there's no cycle, `fast` falls off the end. If there is, both pointers end up circling the loop, and `fast` gains one node per step on `slow`, so it must eventually land exactly on it. It can't jump over `slow`: if `fast` is one behind, the next step brings them together.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        # Two links for every one slow
        # link.
        fast = fast.next.next
        # Compare nodes, not their stored
        # values.
        if slow is fast:
            return True
    return False
```

Note `is`: compare node *identity*, not values. Two different nodes can hold the same value.

### Bound the detection phase

```formula
S ≤ μ + λ
where
S: iterations until an after-movement identity check detects a meeting
μ: tail length, the link steps before the cycle entry
λ: cycle length, the number of nodes around one lap
In words: reaching the cycle takes the tail length, then the one-step relative gain gives a meeting within one additional cycle lap.
```

The first meeting need not be at the entry. In the chain one, two, three, four, five with five linking back to two, the tail is one link and the cycle has four nodes. The pointers first meet at five. In an acyclic chain with three equal values, two different nodes can hold the same value without forming a cycle: identity is what matters. The next unit uses the meeting to locate the entry.

## Key takeaways
- The loop condition determines which even-length middle is returned.
- Detect a cycle by node identity, not repeated values.

## Further reading
- [Cycle detection — Wikipedia](https://en.wikipedia.org/wiki/Cycle_detection)
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
