---
id: dl-detection-recovery-multiple-instances
title: Detecting multi-instance resource deadlock
level: intermediate
minutes: 4
sourceLesson: dl-detection-recovery
summary: Detection compares current requests rather than maximum remaining needs.
---

## Multiple instances: the detection algorithm

With several units per resource type, a cycle is no longer proof (the deadlock fundamentals lessons). The test instead looks like the Banker's safety check, with two changes:

1. Compare each process's **current request**, not its maximum `Need`. Detection asks "can everyone finish given what they're asking for right now?", not "in the worst case".
2. A process holding no units cannot sustain a resource deadlock in this model, so mark it finished. It may still be blocked behind the deadlocked holders.

As in the safety check, a scratch vector `Work` (one number per resource type) starts equal to the free units, and two rules drive the loop:

```formula
Request[i] ≤ Work
Work_new = Work + Allocation[i]
(2, 0, 2) ≤ (3, 1, 3)
Work_new = (3, 1, 3) + (2, 0, 0)
Work_new = (5, 1, 3)
where
i: the unfinished process being checked
Request[i]: the units of each resource type process i is blocked asking for right now; (2, 0, 2) in the example
Work: the units the check treats as free; it starts equal to Available, the units free right now; (3, 1, 3) in the example
Allocation[i]: the units process i holds; (2, 0, 0) in the example
Work_new: Work after process i is treated as finished
≤: less than or equal to, for every resource type
In words: if what a process is waiting for fits in the free pool, assume it finishes and returns everything it holds; whoever is left unfinished when nothing more fits is deadlocked.
```

The example numbers come from the worked example below (P1’s step).

```python
def deadlocked(avail, alloc, request):
    # Nonnegative, matching shapes.
    n = len(alloc)
    # Scratch counts leave the real state
    # intact.
    work = list(avail)
    done = [not any(a) for a in alloc]
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if done[i]:
                continue
            req = request[i]
            if all(r <= w for r, w
                   in zip(req, work)):
                for k in range(len(work)):
                    # Simulate releasing its
                    # units.
                    work[k] += alloc[i][k]
                done[i] = True
                progress = True
    return [i for i in range(n)
            if not done[i]]
```

The optimistic step is "assume a process whose request fits will finish and release everything". If it later asks for more, the next detection run will catch any problem.

### Worked example

Five processes; totals 7 units of A, 2 of B and 6 of C (another Silberschatz example):

```
      Alloc    Request
      A B C    A B C
P0    0 1 0    0 0 0
P1    2 0 0    2 0 2
P2    3 0 3    0 0 0
P3    2 1 1    1 0 0
P4    0 0 2    0 0 2

Available: 0 0 0
```

Every unit is allocated:

```formula
Available = Total − Σ Allocation
Available = (7, 2, 6) − (7, 2, 6)
Available = (0, 0, 0)
where
Total: the units of each resource type that exist: (7, 2, 6)
Σ Allocation: the column sums of Alloc, the units held across all processes: (7, 2, 6)
Σ: add up over every process
Available: the units free now
In words: everything that exists is held by someone, so nothing is free.
```

Nothing is free, which looks alarming. Run the algorithm, starting `Work` at (0, 0, 0):

```
Work     Run   +Alloc
0 0 0    P0    0 1 0
0 1 0    P2    3 0 3
3 1 3    P1    2 0 0
5 1 3    P3    2 1 1
7 2 4    P4    0 0 2
7 2 6    all done
```

(P0 and P2 request nothing, so they go first. The order shown is one valid choice.) No deadlock: everyone can finish.

Now P2 asks for one more C. Rerun from nothing free:

```formula
Request[P2] = (0, 0, 1)
Work = (0, 0, 0) + (0, 1, 0) = (0, 1, 0)
where
Request[P2]: what P2 is now blocked asking for: one unit of C
Work: the units the check treats as free; it starts at (0, 0, 0) and P0 (requesting nothing) finishes first, returning its (0, 1, 0)
In words: after P0 finishes, only one unit of B is free.
```

Now P1 needs A, P2 needs C, P3 needs A and P4 needs C, and `Work` has neither. **P1, P2, P3 and P4 are deadlocked.**

## Key takeaways
- Detection compares current requests rather than maximum remaining needs.
- A process with no allocation cannot sustain this resource deadlock.
- Simulated finishing releases original allocations; unfinished resource holders remain deadlocked under the model.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
