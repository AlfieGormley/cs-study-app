---
id: lin-list-techniques
title: Classic linked-list techniques
level: intermediate
minutes: 13
summary: The handful of pointer patterns behind almost every linked-list problem — in-place reversal, fast and slow pointers (Floyd's cycle detection, finding the middle), merging sorted lists and dummy heads — with traces and proofs.
---

Most linked-list problems, in interviews and in real code, reduce to a few patterns. Learn these four and you can assemble the rest:

1. **Reversal**: turn every arrow around in one pass.
2. **Fast and slow pointers**: two pointers moving at different speeds.
3. **Merging**: weave two sorted lists together.
4. **Dummy heads**: a throwaway node in front so the real head is never a special case.

The iterative patterns below use linear time and **O(1) extra space**; recursive reversal is an explicit exception. Unless detecting a cycle, assume finite acyclic lists. That last part is the point: anyone can solve these problems by copying the list into an array first, but then you've spent O(n) memory.

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

Trace on `1 -> 2 -> 3`:

```
start   prev=None  cur=1   1->2->3
iter 1  None<-1    prev=1  cur=2
iter 2  None<-1<-2 prev=2  cur=3
iter 3  None<-1<-2<-3
        prev=3     cur=None
return 3:  3->2->1
```

Each node is visited once: O(n) time, O(1) space.

### Recursive reversal

```python
def reverse_rec(head):
    if head is None or head.next is None:
        return head
    new_head = reverse_rec(head.next)
    head.next.next = head  # flip
    head.next = None
    return new_head
```

It's elegant, but it uses **O(n) stack space**, one frame per node. In Python the default recursion limit is 1,000, so a 10,000-node list raises `RecursionError`. Prefer the loop.

## Fast and slow pointers

Move one pointer (`slow`) one step at a time and another (`fast`) two steps. The gap between them grows by one each step. That simple fact answers several questions in one pass.

### Finding the middle

When `fast` reaches the end, `slow` has gone half as far.

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

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

The obvious answer is a set of visited nodes: O(n) time but **O(n) memory**. **Floyd's algorithm** (the "tortoise and hare") does it in O(1) memory.

If there's no cycle, `fast` falls off the end. If there is, both pointers end up circling the loop, and `fast` gains one node per step on `slow`, so it must eventually land exactly on it. It can't jump over `slow`: if `fast` is one behind, the next step brings them together.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

Note `is`: compare node *identity*, not values. Two different nodes can hold the same value.

### Finding where the cycle starts

Floyd's algorithm has a second phase. After the pointers meet, put one back at the head and advance **both one step at a time**. They meet again exactly at the first node of the cycle.

```python
def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None        # no cycle
    p = head
    while p is not slow:
        p = p.next
        slow = slow.next
    return p
```

Why does that work? Let:

- **μ** = number of steps from the head to the cycle's start,
- **λ** = the cycle's length,
- **k** = how far into the cycle the pointers meet.

At the first positive-time meeting, slow has walked t = μ + k + jλ steps for some completed laps j ≥ 0, and fast has walked 2t. Their distance difference t is a multiple of λ, so μ + k is also a multiple of λ. This includes μ = 0, where the initial equality is not treated as a detected cycle.

So **μ ≡ −k (mod λ)**. A pointer starting at the meeting point (offset k) that walks μ more steps lands at offset k + μ = mλ, which is the cycle's start. A pointer walking μ steps from the head also lands there. Hence they meet at the start.

> [!example] Trace
> List `1 -> 2 -> 3 -> 4 -> 5 -> 6 -> (back to 3)`, so μ = 2 and λ = 4. Phase 1: slow visits 2, 3, 4, 5 while fast visits 3, 5, 3, 5. They meet at **5** after 4 steps (k = 2). Phase 2: starting from 1 and 5, one step each gives (2, 6), then (3, 3). They meet at **3**, the cycle start, after μ = 2 steps.

To get the cycle's length, hold one pointer at the meeting point and walk the other round until it returns, counting steps.

The same idea finds a duplicate in an array of n + 1 values in the range 1..n, treating each value as a "next" pointer. Brent's algorithm is a variant that typically does fewer pointer moves.

## Dummy heads

Many list operations treat the first node specially: deleting it changes `head`, and building a new list has no node to attach the first element to. A **dummy head** (a sentinel placed before the real head) removes the special case. Build or modify the list after the dummy, then return `dummy.next`.

### Removing the n-th node from the end

Use two pointers with a gap of n between them. When the front one hits the end, the back one is just before the target.

```python
def remove_nth_from_end(head, n):
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be >= 1")
    dummy = Node(0, head)
    front = back = dummy
    for _ in range(n + 1):
        if front is None:
            raise ValueError("n too large")
        front = front.next
    while front:
        front = front.next
        back = back.next
    back.next = back.next.next
    return dummy.next
```

Without the dummy, removing the *first* node (when n equals the length) needs its own branch. With it, `back` simply stays at the dummy and the general code works.

## Merging two sorted lists

Assume two sorted, acyclic, node-disjoint lists and constant-time value comparison. This destructive merge repeatedly takes the smaller head and attaches it to the result. A dummy head gives you somewhere to attach the first node.

```python
def merge(a, b):
    dummy = tail = Node(0)
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b   # leftovers
    return dummy.next
```

```
a: 1 -> 4 -> 6
b: 2 -> 3 -> 7
take 1(a) 2(b) 3(b) 4(a) 6(a)
a empty: attach rest of b (7)
result: 1 2 3 4 6 7
```

This is O(n + m) time and O(1) extra space: it relinks existing nodes rather than creating new ones. Using `<=` keeps equal elements in their original order (a **stable** merge), which matters for merge sort.

Merge is the core of **merge sort on linked lists**, which is the standard way to sort a list in O(n log n) without random access: find the middle with fast/slow pointers, split, sort each half, merge.

## Combining patterns

Harder problems chain these together.

- **Is the list a palindrome, in O(1) space?** Find the middle (fast/slow), reverse the second half, compare the two halves node by node, then reverse it back to restore the list.
- **Reorder `1,2,3,4,5` to `1,5,2,4,3`?** Find the middle, reverse the second half, then interleave the halves.
- **Where do two lists intersect?** Walk pointer A along list A then list B, and pointer B along B then A. Both travel the same total distance, so they arrive at the shared node together (or both reach `None`).

> [!warning] Common bugs
> - Losing the rest of the list by overwriting `next` before saving it.
> - Checking `fast.next.next` without first checking `fast.next`, causing an AttributeError on short lists.
> - Comparing values (`==`) when you mean identity (`is`).
> - Forgetting to restore a list you mutated (for example in the palindrome check), surprising the caller.

## Key takeaways
- Iterative reversal uses `prev`, `cur` and a saved `nxt`: O(n) time, O(1) space. The recursive version uses O(n) stack.
- Fast/slow pointers find the middle in one pass, and detect cycles in O(1) memory (Floyd).
- After Floyd's pointers meet, restart one at the head and step both by one: they meet at the cycle start because μ + k is a multiple of λ.
- A dummy head removes head-of-list special cases in deletion and in building new lists.
- Merging two sorted lists is O(n + m) and stable with `<=`; it's the heart of linked-list merge sort.

## Further reading
- [Cycle detection — Wikipedia](https://en.wikipedia.org/wiki/Cycle_detection)
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [Merge sort — Wikipedia](https://en.wikipedia.org/wiki/Merge_sort)
- [sys.setrecursionlimit — Python docs](https://docs.python.org/3/library/sys.html)
