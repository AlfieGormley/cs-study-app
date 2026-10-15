---
id: fp-persistent-queue-costs
title: Persistent queues and replayed work
level: advanced
minutes: 4
sourceLesson: fp-persistent-data
summary: A two-list queue has a simple amortised bound along one version history.
---

A two-list queue has a simple amortised bound along one version history. This unit develops that mechanism using the earlier units as prerequisites.

## Amortisation breaks under persistence

The classic functional queue keeps two lists: `front` for popping and `back` for pushing (newest first). When `front` runs out, reverse `back` into a new `front`:

```python
# Reverse only when the front is empty.
def push(q, x):
    front, back = q
    return front, (x, back)

def pop(q):
    front, back = q
    if front is None:
        while back is not None:
            x, back = back
            front = (x, front)
    if front is None:
        raise IndexError("empty queue")
    x, rest = front
    return x, (rest, back)
```

Each list is a nested (head, tail) tuple ending in None, as above; the empty queue is (None, None). Both prepend and tail access are O(1).

Used normally, each element is reversed once, so the costs average out to O(1) per operation: a fixed cost however long the queue. That's an **amortised** bound (an **amortised cost**): occasional expensive reverses are paid for by many cheap pushes.

```formula
T_total ≤ 2m
T_avg = T_total / m ≤ 2
where
T_total: the total number of basic steps (one per push, one per element moved by a reverse, one per pop) for a sequence starting from an empty queue and always using the latest returned version; count successful operations only
m: the number of push and pop operations in the sequence
T_avg: the average (amortised) cost per operation
≤: less than or equal to
In words: each element is pushed once, moved by a reverse at most once and popped once, so the whole sequence costs at most about two steps per operation, however unevenly those steps fall.
```

For example, 1,000 pushes followed by 1,000 pops cost 1,000 push steps, one 1,000-step reverse and 1,000 pop steps: 3,000 steps for two thousand operations, an average of 1.5.

Persistence breaks the argument. Take a version `q` whose `front` is empty and whose `back` holds n items. If you call `pop(q)` a thousand times (on the *same* old version, which persistence explicitly allows), each call does the full O(n) reverse. The "savings" from cheap pushes were spent once, but the expensive step is replayed every time.

```formula
T_replay = k × n
T_replay = 1000 × 1000 = 1000000
where
T_replay: the total reversal steps when pop is called k times on the same old version
k: the number of pops on that one version
n: the number of items in its back list
In words: every pop on the old version redoes the full reverse, so the cost is k times n rather than n once.
```

A thousand items and a thousand repeated pops on that same version therefore cause a million reversal steps instead of one shared thousand-step reversal.

Chris Okasaki's fix, in *Purely Functional Data Structures*, is to combine persistence with **laziness**: arrange lazy memoized work so branches share one thunk (suspended computation) created before they diverge. Creating a fresh thunk in each pop would still repeat the reversal. Appropriate invariants recover amortised bounds; incremental rotation and scheduling are additionally needed for worst-case O(1).

> [!warning] Rule of thumb
> If a persistent structure's docs say "amortised", check whether that bound holds when old versions are reused. Okasaki-style structures are designed for it; a naive port of a mutable algorithm usually isn't.

## Key takeaways
- A two-list queue has a simple amortised bound along one version history.
- Reusing an old version can replay an unshared reversal.

## Further reading
- [Okasaki: Purely Functional Data Structures](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf)
