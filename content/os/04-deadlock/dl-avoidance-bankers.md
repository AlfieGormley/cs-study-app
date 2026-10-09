---
id: dl-avoidance-bankers
title: Avoidance and the Banker's algorithm
level: intermediate
minutes: 12
summary: Safe and unsafe states, and Dijkstra's Banker's algorithm worked through with real matrices, plus the practical assumptions that limit its use.
---

Prevention changes the rules so deadlock can't happen. **Avoidance** keeps the normal rules but looks ahead: before granting each request, the system asks "if I say yes, can I still guarantee that everyone finishes?" If not, the requester waits, even when the resources are free right now.

The classic avoidance scheme is Edsger Dijkstra's **Banker's algorithm**, from the mid-1960s.

## The intuition: a cautious bank

A small bank has £10 to lend. Three customers each have an agreed credit limit, and each will repay everything once they have borrowed up to their limit and finished their project.

| Customer | Limit | Borrowed | Could still ask for |
|---|---|---|---|
| Ann | £8 | £4 | £4 |
| Bob | £3 | £2 | £1 |
| Cat | £7 | £2 | £5 |

The bank has lent £8, so £2 is in the vault.

Is the bank safe? It can give Bob his remaining £1, Bob finishes and repays £3, so the vault has £4. That covers Ann's £4; she repays £8, giving £8 in the vault, enough for Cat's £5. Everyone can finish in the order **Bob, Ann, Cat**.

Now Cat asks for £1. The vault has £2, so the bank *could* hand it over. But then the vault holds £1. Bob can finish (needs £1) and repays £3, so the vault has £3. Ann still needs £4 and Cat now needs £4. Nobody else can finish. If both insist on their full limits, the bank is stuck.

So the bank tells Cat to wait. That is the whole idea of avoidance.

## Safe, unsafe and deadlocked

A state is **safe** if there is at least one order (a **safe sequence**) in which every process can get its maximum remaining need, using what's free plus what earlier processes in the sequence release.

```
+-------------------------------+
|  all states                   |
|  +-------------------------+  |
|  |  unsafe                 |  |
|  |   +-----------------+   |  |
|  |   |   deadlocked    |   |  |
|  |   +-----------------+   |  |
|  +-------------------------+  |
|  safe (everything outside)    |
+-------------------------------+
```

- Every deadlocked state is unsafe.
- An unsafe state is **not necessarily** deadlocked. It means the system can no longer *guarantee* completion: if processes happen to ask for their maximums, deadlock follows. They might not.
- The Banker's algorithm keeps the system in safe states only. That's sufficient to avoid deadlock, but it's conservative: it refuses some requests that would have turned out fine.

## What the algorithm needs

The algorithm counts resources in units: one lock, one tape drive, one buffer. Units of the same **resource type** are interchangeable, so a process asks for "two of type B", not for a particular one.

It writes these counts as lists with one number per resource type. With three types A, B and C, the list (7, 5, 3) means 7 of A, 5 of B and 3 of C. Such a list is a **vector**, and a table of vectors with one row per process is a **matrix**.

With n processes and m resource types, the algorithm keeps four of these structures:

| Structure | Shape | Meaning |
|---|---|---|
| `Available` | m numbers | Free units of each type |
| `Max` | n rows of m | Most each process may ever hold |
| `Allocation` | n rows of m | Currently held |
| `Need` | n rows of m | What each may still ask for |

`Need` is not declared by anyone; it is worked out from the other two, one entry at a time:

```formula
Need[i][j] = Max[i][j] − Allocation[i][j]
Need[P0][B] = 5 − 1 = 4
where
i: the process, numbered from 0 to n − 1 (P0, P1, …)
j: the resource type (A, B, C, … up to m types)
n: the number of processes
m: the number of resource types
Max[i][j]: the most units of type j that process i has declared it may ever hold at once
Allocation[i][j]: the units of type j that process i holds right now
Need[i][j]: the units of type j that process i may still ask for before it finishes
P0: process number 0
B: resource type B; in the example P0 has declared at most 5 units of B and holds 1
In words: what a process may still request is its declared maximum minus what it already has.
```

So a process that declared at most 5 units of B and already holds 1 may ask for 4 more. Doing this for every entry gives the whole `Need` matrix. The formula only makes sense if no process ever holds more than it declared, which the request algorithm below enforces.

The crucial requirement is `Max`: each process must **declare its maximum claim up front**. That is also the algorithm's biggest practical weakness.

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
2. Find an unfinished process `i` whose `Need[i] ≤ Work` holds for every resource type.
3. Pretend it runs to completion: add `Allocation[i]` to `Work`, and mark it finished. Go to step 2.
4. If no such process exists: the state is safe if and only if every process is finished.

Step 3 adds the process's **allocation**, not its need, because the process releases everything it holds when it finishes, including the extra it was just "lent". In the example, the process needed (1, 2, 2) more, held (2, 0, 0), and its finishing raises `Work` from (3, 3, 2) to (5, 3, 2).

```python
def is_safe(avail, alloc, need):
    # Validated nonnegative inputs.
    # All rows have len(avail) components.
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
                    work[r] += alloc[i][r]
                done[i] = True
                order.append(i)
                progress = True
    return all(done), order
```

Picking greedily is fine: finishing a process only ever *adds* to `Work`, so finishing someone early can never stop someone else finishing later. You never need to backtrack.

**Cost.** Each pass over the processes looks at up to n of them, and each look compares m numbers. Every pass that doesn't stop finishes at least one process, so there are at most n passes:

```formula
C ≤ n × n × m = m × n^2
C ≤ 10 × 1000^2 = 10^7
T_check = O(m × n^2)
where
C: the worst-case number of single-number comparisons in one safety check
n: the number of processes; 1000 in the example
m: the number of resource types; 10 in the example
T_check: the running time of one safety check
O(…): big O: grows no faster than the expression inside, ignoring constant factors
In words: the check can take up to n passes of n processes with m comparisons each, so doubling the number of processes roughly quadruples the worst-case work.
```

For the five-process, three-type example below that is at most 3 × 5² = 75 comparisons, which is nothing. For 1,000 processes and 10 types it is up to 10 million comparisons on every request. It is a loose upper bound: finished processes are skipped and a comparison stops at the first resource type that doesn't fit.

## The request algorithm

When a process asks for more units, the system makes two comparisons and, if both pass, three trial updates:

```formula
Request ≤ Need[p]
Request ≤ Available
Available_new = Available − Request
Allocation_new[p] = Allocation[p] + Request
Need_new[p] = Need[p] − Request
where
p: the process making the request
Request: the vector of extra units p asks for now, one number per resource type
Need[p]: the units p may still request under its declared maximum
Available: the vector of units free right now
Allocation[p]: the units p holds now
Available_new, Allocation_new[p], Need_new[p]: the trial ("pretend") values if the request were granted
≤: less than or equal to, checked for every resource type
In words: a request must fit inside the process's remaining claim and inside what is free; if it does, move those units from the free pool to the process on paper, then test the result.
```

The request algorithm:

1. If `Request ≤ Need[p]` fails for any resource type: error. The process has exceeded its declared maximum.
2. If `Request ≤ Available` fails for any resource type: `p` must wait; the resources simply aren't there.
3. Otherwise, **pretend to grant it** by making the three updates.
4. Run the safety algorithm on the pretend state. Safe: make it real. Unsafe: roll back and make `p` wait.

The worked example below runs exactly these steps with real numbers.

```python
def request(p, req, avail, alloc, need):
    if len(req) != len(avail):
        raise ValueError("request width")
    if any(x < 0 for x in req):
        raise ValueError("negative request")
    m = range(len(req))
    if any(req[r] > need[p][r] for r in m):
        raise ValueError("over max claim")
    if any(req[r] > avail[r] for r in m):
        return "wait"
    # pretend to grant, then test
    a = [avail[r] - req[r] for r in m]
    al = [row[:] for row in alloc]
    nd = [row[:] for row in need]
    for r in m:
        al[p][r] += req[r]
        nd[p][r] -= req[r]
    safe, _ = is_safe(a, al, nd)
    return "grant" if safe else "wait"
```

This request function returns a decision on copied state; it does not commit a grant. A real allocator must serialize the check and state update, validate process IDs and matrix dimensions, and manage waiting requests.

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
4. Safety check from `Work` = (2, 3, 0): P1 needs (0, 2, 0), fits, and `Work` becomes (5, 3, 2). From there, P3, P4, P0, P2 finish exactly as before.

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

## Single-instance resources: the claim-edge graph

If every resource has one instance, there's a cheaper variant using the resource-allocation graph. Each process declares in advance which resources it may request; these appear as dashed **claim edges** `P - - > R`. A request turns a claim edge into a request edge, and it's granted only if converting it to an assignment edge `R → P` creates **no cycle** (counting claim edges). A graph traversal detects cycles in O(V + E), where V is the number of vertices (processes plus resources) and E the number of edges; a dense adjacency-matrix representation can take O(V²).

## Practical limitations

Using this safety test as a general resource manager requires strong assumptions:

- **Max claims are unknown.** A web server thread has no idea how many locks, buffers or file handles it will need.
- **The population changes.** Processes and threads come and go constantly; new claims must be registered and checked against the safety invariant. A changing population is additional bookkeeping, not a fundamental prohibition.
- **Resources change.** Devices fail and memory gets hot-plugged.
- **It's conservative.** Unsafe isn't deadlocked, so it refuses requests that would have been fine, wasting capacity.
- **It's expensive.** O(m·n²) on every request, where n is the number of processes and m the number of resource types, is a lot with thousands of threads.
- **It needs every holder to finish.** A process holding resources while waiting for user input breaks the "everyone eventually completes" assumption.

The *idea* lives on as **admission control**: reserve a worst-case budget before starting work, and refuse or queue requests that would overcommit.

- The Kubernetes scheduler places a pod only on a node whose unreserved capacity covers the pod's declared resource *requests*.
- Linux with `vm.overcommit_memory=2` refuses allocations that would push committed memory past a commit limit, rather than overcommitting and relying on the OOM killer later.
- Connection pools that cap each client at a fixed number of connections stop one client from holding them all.

None is the full Banker's algorithm. They illustrate admission or capacity checks, but Kubernetes requests are scheduling reservations rather than maximum usage claims, and a per-client connection cap alone does not prove pool deadlock freedom.

> [!note] Content gap
> No reproducible runtime benchmark or survey of production adoption accompanies this lesson. Complexity describes the shown algorithm, not a measured duration or proof that all admission-control systems implement it.

## Key takeaways
- Avoidance grants a request only if the resulting state is safe: some order exists in which every process can finish.
- Unsafe means deadlock is possible, not certain; deadlocked states are a subset of unsafe ones.
- The Banker's algorithm needs `Available`, `Max`, `Allocation` and `Need` (each process's `Max` minus its `Allocation`), and costs O(m·n²) per check for n processes and m resource types.
- In the safety check, a finished process gives back its allocation; greedy selection never needs backtracking.
- A request can be refused even when the resources are free, if granting it would make the state unsafe.
- Unknown maximum claims and changing populations complicate direct use; admission control shares the idea of reserving capacity before accepting work.

## Further reading
- [Banker's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Banker%27s_algorithm)
- [Deadlock (computer science): avoidance — Wikipedia](https://en.wikipedia.org/wiki/Deadlock_(computer_science))
- [OSTEP: Common Concurrency Problems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
