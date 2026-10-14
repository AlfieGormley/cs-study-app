---
id: lin-list-cycle-entry-proof
title: Locate the entry of a detected cycle
level: intermediate
minutes: 5
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

Why does that work? Name three distances. By convention they use Greek letters: **μ** (mu) and **λ** (lambda).

The first card defines these distances in link steps and nodes. They are not memory addresses.

Count the steps each pointer has walked when they first meet (not counting the start, where both sit on the head). Slow reaches the cycle after μ steps, goes some number of whole laps, then k more. Fast moves twice as fast, so it has walked twice as far:

```formula
t = μ + k + jλ
2t − t = qλ
μ + k + jλ = qλ
μ + k = (q − j)λ = mλ
where
t: the number of steps slow has taken when the pointers first meet; fast has taken 2t steps by then
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

In the trace below the tail is two links long and the meeting is two links into a four-node cycle. Both two and negative two have remainder two modulo four, so the rule holds. A pointer walking μ steps from the head also lands on the cycle's start. Both pointers move one step at a time, so they arrive together, and the first node where they meet is the start. The argument also covers a zero-length tail, where the cycle starts at the head; there the initial equality at the head is not treated as a detected cycle.

The trace below checks the numbers: the tail is 2 steps and the pointers meet 2 steps into a 4-node cycle, and 2 + 2 = 4 is exactly one lap.

> [!example] Trace
> List `1 -> 2 -> 3 -> 4 -> 5 -> 6 -> (back to 3)`, so the tail μ is 2 steps and the cycle length λ is 4. Phase 1: slow visits 2, 3, 4, 5 while fast visits 3, 5, 3, 5. They meet at **5** after 4 steps, 2 steps into the cycle (k is 2). Phase 2: starting from 1 and 5, one step each gives (2, 6), then (3, 3). They meet at **3**, the cycle start, after μ (2) steps.

To get the cycle's length, hold one pointer at the meeting point and walk the other round until it returns, counting steps.

The same idea finds a duplicate in an array of n + 1 values, each between 1 and n, treating each value as a "next" pointer. Brent's algorithm is a variant that typically does fewer pointer moves.

## Key takeaways
- At a meeting, the fast pointer has gained a whole number of cycle laps.
- Reset one pointer to the head and move both one link per step.

## Further reading
- [Cycle detection — Wikipedia](https://en.wikipedia.org/wiki/Cycle_detection)
