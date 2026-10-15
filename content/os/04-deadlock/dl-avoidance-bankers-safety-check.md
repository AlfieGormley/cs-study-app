---
id: dl-avoidance-bankers-safety-check
title: Checking for a safe sequence
level: intermediate
minutes: 4
sourceLesson: dl-avoidance-bankers
summary: The scratch Work vector grows by a finishing process’s original allocation.
---

## The safety algorithm

To test whether a state is safe, the algorithm keeps a scratch vector called `Work`: the units that would be free if every process finished so far had handed back what it holds. Two rules drive it. The first decides whether a process can finish; the second updates `Work` when it does:

```formula
Need[i] ≤ Work
Work_new = Work + Allocation[i]
(1, 2, 2) ≤ (3, 3, 2)
Work_new = (3, 3, 2) + (2, 0, 0)
Work_new = (5, 3, 2)
where
i: the unfinished process being checked
Need[i]: process i's row of Need: for each resource type, the units it may still request; (1, 2, 2) in the example
Work: a vector, one number per resource type, of units the check treats as free; it starts equal to Available, the units free right now; (3, 3, 2) in the example
Allocation[i]: process i's row of Allocation: the units it holds now; (2, 0, 0) in the example
Work_new: the value of Work after process i is treated as finished
≤: less than or equal to; between two vectors it must hold for every resource type, so (1, 2, 2) ≤ (3, 3, 2) is true but (1, 2, 2) ≤ (3, 1, 2) is false
In words: a process can be allowed to finish if every number in its remaining need fits in what is free; once it finishes, everything it was holding goes back into the free pool.
```

The full procedure:

1. Set `Work` equal to `Available`. Mark every process unfinished.
2. Find an unfinished process whose remaining need fits inside Work for every resource type.
3. Pretend it runs to completion: add `Allocation[i]` to `Work`, and mark it finished. Go to step 2.
4. If no such process exists: the state is safe if and only if every process is finished.

Step 3 adds the process's **allocation**, not its need, because the process releases everything it holds when it finishes, including the extra it was just "lent". In the example, the process needed (1, 2, 2) more, held (2, 0, 0), and its finishing raises `Work` from (3, 3, 2) to (5, 3, 2).

```python
def is_safe(avail, alloc, need):
    # Validated nonnegative inputs.
    # All rows have len(avail) components.
    # Scratch counts leave the real state
    # intact.
    work = list(avail)
    done = [False] * len(alloc)
    order = []
    progress = True
    while progress:
        progress = False
        for i in range(len(alloc)):
            if done[i]:
                continue
            if all(n <= w for n, w
                   in zip(need[i], work)):
                for r in range(len(work)):
                    # Return its held units.
                    work[r] += alloc[i][r]
                done[i] = True
                order.append(i)
                progress = True
    return all(done), order
```

Picking greedily is fine: finishing a process only ever *adds* to `Work`, so finishing someone early can never stop someone else finishing later. You never need to backtrack.

**Cost.** Each pass checks unfinished processes across the resource types. Each productive pass finishes at least one process; a final unsuccessful pass makes no component comparisons if all processes are already finished. Let n count processes and m count resource types:

```formula
C ≤ mn^2
C ≤ 10 × 1000^2 = 10^7
T_check = O(mn^2)
where
C: the worst-case number of single-number comparisons in one safety check
n: the number of processes; 1000 in the example
m: the number of resource types; 10 in the example
T_check: the running time of one safety check
O(…): big O: grows no faster than the expression inside, ignoring constant factors
In words: the check can take up to n passes of n processes with m comparisons each, so doubling the number of processes roughly quadruples the worst-case work.
```

For the five-process, three-type matrix example in the following lessons that is at most 3 × 5² = 75 comparisons, which is nothing. For 1,000 processes and 10 types it is up to 10 million comparisons on every request. It is a loose upper bound: finished processes are skipped and a comparison stops at the first resource type that doesn't fit.

## Key takeaways
- The scratch Work vector grows by a finishing process’s original allocation.
- Greedy selection needs no backtracking because finishing cannot reduce available capacity.
- The repeated-scan implementation has a quadratic process-count upper bound.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
