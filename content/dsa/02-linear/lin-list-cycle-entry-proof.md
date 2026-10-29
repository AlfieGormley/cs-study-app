---
id: lin-list-cycle-entry-proof
title: Locate the entry of a detected cycle
level: intermediate
minutes: 4
sourceLesson: lin-list-techniques
summary: At a meeting, the fast pointer has gained a whole number of cycle laps.
---

First detect a meeting with the one-step slow pointer and two-step fast pointer. The preceding unit covered that identity test. This unit locates the cycle’s first node and proves why resetting one pointer works; no auxiliary set or list copying is required.

### Finding where the cycle starts

Floyd's algorithm has a second phase. After the pointers meet, put one back at the head and advance **both one step at a time**. They meet again exactly at the first node of the cycle.

```python
def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        # Two links for every one slow
        # link.
        fast = fast.next.next
        # Compare nodes, not their stored
        # values.
        if slow is fast:
            break
    else:
        return None        # no cycle
    # Reset only one pointer after meeting.
    p = head
    while p is not slow:
        p = p.next
        slow = slow.next
    return p
```

Why does that work? Name three distances, by convention with Greek letters: **μ** (mu) is the tail length from the head to the cycle's first node, **λ** (lambda) is the number of nodes in the cycle, and k is how far past the cycle's first node the pointers met. These count link steps and nodes, not memory addresses.

When they first meet, fast has walked twice as far as slow, yet they stand on the same node. Fast's extra distance must therefore be a whole number of laps. Slow's distance is the tail, some whole laps and then k more, which leads to the key relationship:

```formula essential
t = μ + k + jλ
2t − t = qλ
μ + k = (q − j)λ = mλ
where
t: the number of steps slow has taken when the pointers first meet; fast has taken 2t steps by then
μ: mu, the number of steps from the head to the first node of the cycle
k: how many steps past the cycle's first node the meeting point is (0 up to λ − 1)
λ: lambda, the number of nodes in the cycle
j: how many complete laps of the cycle slow made before meeting (0 or more)
q: how many whole laps fast is ahead of slow at the meeting
m: the whole number q − j (0 or more; it is 0 only when the cycle starts at the head and they meet there)
In words: fast's extra distance is a whole number of laps, so the tail length plus the meeting offset is a whole number of laps too.
```

The last line is the key. Walking μ steps forward from the meeting point means being μ + k steps past the cycle's start in total: a whole number of laps, so it lands exactly back on the start. Meanwhile a pointer walking μ steps from the head also arrives at the start. Both move one step at a time, so the first node where they meet is the cycle's start. The argument also covers a zero-length tail, where the cycle starts at the head; there the initial equality at the head is not treated as a detected cycle.

> [!example] Trace
> List `1 -> 2 -> 3 -> 4 -> 5 -> 6 -> (back to 3)`: a two-step tail and a four-node cycle. Phase 1: slow visits 2, 3, 4, 5 while fast visits 3, 5, 3, 5. They meet at **5** after 4 steps, 2 steps into the cycle. Tail plus offset is four steps, exactly one lap. Phase 2: starting from 1 and 5, one step each gives (2, 6), then (3, 3). They meet at **3**, the cycle start, after two steps: the tail length.

To get the cycle's length, hold one pointer at the meeting point and walk the other round until it returns, counting steps.

The same idea finds a duplicate in an array of n + 1 values, each between 1 and n, treating each value as a "next" pointer. Brent's algorithm is a variant that typically does fewer pointer moves.

## Key takeaways
- At a meeting, the fast pointer has gained a whole number of cycle laps.
- Reset one pointer to the head and move both one link per step.

## Further reading
- [Cycle detection — Wikipedia](https://en.wikipedia.org/wiki/Cycle_detection)
