---
id: dl-avoidance-bankers-matrix-sequence
title: Tracing a matrix safety check
level: intermediate
minutes: 3
sourceLesson: dl-avoidance-bankers
summary: Free resources are totals minus column allocations.
---

## Worked example with matrices

Five processes, three resource types. Totals: 10 units of A, 5 of B and 7 of C. (This is the standard textbook example from Silberschatz's *Operating System Concepts*.)

```
      Alloc    Max      Need
      A B C    A B C    A B C
P0    0 1 0    7 5 3    7 4 3
P1    2 0 0    3 2 2    1 2 2
P2    3 0 2    9 0 2    6 0 0
P3    2 1 1    2 2 2    0 1 1
P4    0 0 2    4 3 3    4 3 1

Allocated: 7 2 5   Available: 3 3 2
```

The free units are whatever exists minus whatever is held, and each `Need` row is that process's `Max` row minus its `Alloc` row:

```formula
Available[j] = Total[j]
  − Σ_i Allocation[i][j]
Available = (10, 5, 7) − (7, 2, 5)
Available = (3, 3, 2)
Need[P0] = (7, 5, 3) − (0, 1, 0)
Need[P0] = (7, 4, 3)
where
j: a resource type: A, B or C
i: a process, P0 to P4
Total[j]: how many units of type j exist; (10, 5, 7) here
Allocation[i][j]: the units of type j that process i holds (the Alloc column)
Σ_i: add up over every process i: here, the column sum of Alloc, (7, 2, 5)
Available[j]: the units of type j free right now
Need[P0]: process P0's remaining need: its Max row (7, 5, 3) minus its Alloc row (0, 1, 0)
In words: free units are total units minus the units held; a process's need is its declared maximum minus what it holds.
```

The other `Need` rows come out the same way, which is how the right-hand block of the table was filled in.

### Is it safe?

Run the safety algorithm, scanning P0 to P4 each pass. P0 is checked first and fails: it needs 7 units of A and only 3 are free. P1 is next:

```formula
(1, 2, 2) ≤ (3, 3, 2)
Work = (3, 3, 2) + (2, 0, 0) = (5, 3, 2)
where
Work: the units the check treats as free; it starts at Available, (3, 3, 2)
≤: less than or equal to, for every resource type: P1's need (1, 2, 2) fits inside (3, 3, 2) in A, B and C
In words: P1 can be finished, and when it finishes it hands back its allocation (2, 0, 0), so the free pool grows to (5, 3, 2).
```

Each row of the table below is one such check: the current `Work`, the process and its `Need`, and whether it fits. "+2 0 0" is the allocation added back when it does:

```
Work     Check           Result
3 3 2    P0 7 4 3        no (A)
3 3 2    P1 1 2 2        yes  +2 0 0
5 3 2    P2 6 0 0        no (A)
5 3 2    P3 0 1 1        yes  +2 1 1
7 4 3    P4 4 3 1        yes  +0 0 2
7 4 5    P0 7 4 3        yes  +0 1 0
7 5 5    P2 6 0 0        yes  +3 0 2
10 5 7   all finished
```

Safe, with sequence **P1, P3, P4, P0, P2**. Note `Work` ends at the totals (10, 5, 7), a handy check on your arithmetic. Other safe sequences exist too (for instance P3, P1, P4, P2, P0); you only need one.

## Key takeaways
- Free resources are totals minus column allocations.
- The shown scan produces P1, P3, P4, P0, P2; other safe sequences can exist.
- The final Work vector equals the resource totals.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
