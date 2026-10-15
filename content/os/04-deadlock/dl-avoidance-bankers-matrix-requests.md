---
id: dl-avoidance-bankers-matrix-requests
title: Granting one request and delaying another
level: intermediate
minutes: 3
sourceLesson: dl-avoidance-bankers
summary: Granting P1’s request retains a safe sequence.
---

### P1 requests (1, 0, 2)

The request algorithm's checks and trial updates, with the numbers filled in:

```formula
(1, 0, 2) ≤ Need[P1] = (1, 2, 2)
(1, 0, 2) ≤ Available = (3, 3, 2)
Available = (3, 3, 2) − (1, 0, 2)
Available = (2, 3, 0)
Allocation[P1] = (2, 0, 0) + (1, 0, 2)
Allocation[P1] = (3, 0, 2)
Need[P1] = (1, 2, 2) − (1, 0, 2)
Need[P1] = (0, 2, 0)
Work = (2, 3, 0) + (3, 0, 2) = (5, 3, 2)
where
P1: process number 1, which is asking for (1, 0, 2): one A, no B, two C
Need[P1]: the units P1 may still ask for
Available: the units free right now
Allocation[P1]: the units P1 holds
Work: the units the safety check treats as free; it starts at the new Available
≤: less than or equal to, for every resource type
In words: the request fits P1's claim and what is free; after the trial grant P1 itself can finish at once and hand back (3, 0, 2).
```

1. The request is within P1's remaining claim.
2. The units are free.
3. Pretend to grant it: the trial `Available`, `Allocation[P1]` and `Need[P1]` are the values above.
4. Safety check with a starting Work vector of (2, 3, 0): P1 needs (0, 2, 0), fits, and `Work` becomes (5, 3, 2). From there, P3, P4, P0, P2 finish exactly as before.

Safe, so **grant**.

### Then P0 requests (0, 2, 0)

```formula
(0, 2, 0) ≤ Need[P0] = (7, 4, 3)
(0, 2, 0) ≤ Available = (2, 3, 0)
Available = (2, 3, 0) − (0, 2, 0)
Available = (2, 1, 0)
Allocation[P0] = (0, 1, 0) + (0, 2, 0)
Allocation[P0] = (0, 3, 0)
Need[P0] = (7, 4, 3) − (0, 2, 0)
Need[P0] = (7, 2, 3)
where
P0: process number 0, asking for (0, 2, 0): two units of B
Need[P0]: the units P0 may still ask for
Available: the units free right now (after P1's grant)
Allocation[P0]: the units P0 holds
≤: less than or equal to, for every resource type
In words: the request is valid and the units are free, so the system pretends to grant it and then tests the result.
```

1. The request is within P0's claim of (7, 4, 3): fine.
2. The two units of B are free: fine.
3. Pretend to grant it, giving the trial values above.
4. Safety check, starting `Work` at the trial `Available`, (2, 1, 0):

```
P0 7 2 3   no (A)
P1 0 2 0   no (B: 2 > 1)
P2 6 0 0   no (A)
P3 0 1 1   no (C: 1 > 0)
P4 4 3 1   no
```

No process can finish. Unsafe, so P0 **waits**, even though the two units of B it asked for are sitting free.

### And P4 requests (3, 3, 0)

Available is (2, 3, 0) and 3 > 2 for A. Step 2 fails: P4 waits because the resources simply aren't there. No safety check needed.

## Key takeaways
- Granting P1’s request retains a safe sequence.
- P0’s subsequent request fits free capacity but makes every remaining process unable to finish.
- P4’s request exceeds currently free A units, so no safety check is needed.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
