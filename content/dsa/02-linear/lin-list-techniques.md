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

Trace on `1 -> 2 -> 3`:

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
    new_head = reverse_rec(head.next)
    head.next.next = head  # flip
    head.next = None
    return new_head
```

It's elegant, but on an n-node list it uses **O(n) stack space**, one frame per node. In Python the default recursion limit is 1,000, so a 10,000-node list raises `RecursionError`. Prefer the loop.

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

The obvious answer is a set of visited nodes: for a list of n nodes that is O(n) time but **O(n) memory**. **Floyd's algorithm** (the "tortoise and hare") does it in O(1) memory.

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

Why does that work? Name three distances. By convention they use Greek letters: **μ** (mu) and **λ** (lambda).

- **μ** = number of steps from the head to the cycle's start (the length of the "tail" before the loop),
- **λ** = the cycle's length, in nodes,
- **k** = how far into the cycle, counting from its start, the pointers meet.

Count the steps each pointer has walked when they first meet (not counting the start, where both sit on the head). Slow reaches the cycle after μ steps, goes some number of whole laps, then k more. Fast moves twice as fast, so it has walked twice as far:

```formula
t = μ + k + j × λ
2 × t − t = q × λ
μ + k + j × λ = q × λ
μ + k = (q − j) × λ = m × λ
where
t: the number of steps slow has taken when the pointers first meet; fast has taken 2 × t steps by then
q: how many whole laps fast is ahead of slow at the meeting (they are on the same node, so fast's extra t steps must be whole laps)
μ: mu, the number of steps from the head to the first node of the cycle
k: how many steps past the cycle's first node the meeting point is (0 up to λ − 1)
λ: lambda, the number of nodes in the cycle
j: how many complete laps of the cycle slow made before meeting (0 or more)
m: the whole number q − j (0 or more; it is 0 only when the cycle starts at the head and they meet there)
In words: both pointers are on the same node, so fast's extra distance is a whole number of laps; that forces the tail length plus the meeting offset to be a whole number of laps too.
```

The last line is the key. Walking μ steps forward from the meeting point means walking μ + k steps from the cycle's start in total, which is a whole number of laps, so it lands exactly back on the cycle's start. Mathematicians write the same fact using **modular arithmetic** (arithmetic on remainders, like a clock face):

```formula
μ ≡ −k (mod λ)
where
μ: mu, the number of steps from the head to the cycle's start
k: how many steps past the cycle's start the pointers met
λ: lambda, the number of nodes in the cycle
≡: is congruent to: both sides leave the same remainder when divided by the number after mod
mod: modulo: (mod λ) means "comparing remainders after dividing by λ", i.e. ignoring whole laps
In words: walking μ steps on from the meeting point has the same effect as stepping k back, which is exactly the cycle's start.
```

In the trace below, μ = 2, k = 2 and λ = 4: 2 and −2 both leave remainder 2 when divided by 4 (because −2 = −1 × 4 + 2), so the rule holds. A pointer walking μ steps from the head also lands on the cycle's start. Both pointers move one step at a time, so they arrive together, and the first node where they meet is the start. The argument also covers μ = 0, a cycle that starts at the head; there the initial equality at the head is not treated as a detected cycle.

The trace below checks the numbers: the tail is 2 steps and the pointers meet 2 steps into a 4-node cycle, and 2 + 2 = 4 is exactly one lap.

> [!example] Trace
> List `1 -> 2 -> 3 -> 4 -> 5 -> 6 -> (back to 3)`, so the tail μ is 2 steps and the cycle length λ is 4. Phase 1: slow visits 2, 3, 4, 5 while fast visits 3, 5, 3, 5. They meet at **5** after 4 steps, 2 steps into the cycle (k is 2). Phase 2: starting from 1 and 5, one step each gives (2, 6), then (3, 3). They meet at **3**, the cycle start, after μ (2) steps.

To get the cycle's length, hold one pointer at the meeting point and walk the other round until it returns, counting steps.

The same idea finds a duplicate in an array of n + 1 values, each between 1 and n, treating each value as a "next" pointer. Brent's algorithm is a variant that typically does fewer pointer moves.

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

For lists of n and m nodes, this is O(n + m) time and O(1) extra space: it relinks existing nodes rather than creating new ones. Using `<=` keeps equal elements in their original order (a **stable merge**), which matters for merge sort.

Merge is the core of **merge sort on linked lists**, which is the standard way to sort an n-node list in O(n log n) without random access (log n is log₂ n, the number of times n can be halved before reaching 1; it is how many levels of splitting there are): find the middle with fast/slow pointers, split, sort each half, merge.

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
- Iterative reversal uses `prev`, `cur` and a saved `nxt`: O(n) time, O(1) space for n nodes. The recursive version uses O(n) stack.
- Fast/slow pointers find the middle in one pass, and detect cycles in O(1) memory (Floyd).
- After Floyd's pointers meet, restart one at the head and step both by one: they meet at the cycle start because the tail length plus the meeting offset is a whole number of laps of the cycle.
- A dummy head removes head-of-list special cases in deletion and in building new lists.
- Merging two sorted lists of n and m nodes is O(n + m) and stable with `<=`; it's the heart of linked-list merge sort.

## Further reading
- [Cycle detection — Wikipedia](https://en.wikipedia.org/wiki/Cycle_detection)
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [Merge sort — Wikipedia](https://en.wikipedia.org/wiki/Merge_sort)
- [sys.setrecursionlimit — Python docs](https://docs.python.org/3/library/sys.html)
