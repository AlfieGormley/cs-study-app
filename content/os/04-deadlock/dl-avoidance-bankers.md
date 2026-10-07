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

With `n` processes and `m` resource types:

| Structure | Shape | Meaning |
|---|---|---|
| `Available` | m | Free units of each type |
| `Max` | n × m | Most each process may ever hold |
| `Allocation` | n × m | Currently held |
| `Need` | n × m | `Max − Allocation` |

The crucial requirement is `Max`: each process must **declare its maximum claim up front**. That is also the algorithm's biggest practical weakness.

## The safety algorithm

To test whether a state is safe:

1. Set `Work = Available`. Mark every process unfinished.
2. Find an unfinished process `i` with `Need[i] ≤ Work` (every component).
3. Pretend it runs to completion: `Work += Allocation[i]`, mark it finished. Go to step 2.
4. If no such process exists: the state is safe if and only if every process is finished.

Step 3 adds the process's **allocation**, not its need, because the process releases everything it holds when it finishes, including the extra it was just "lent".

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

**Cost**: each pass is O(n·m) and you need at most n passes, so O(m·n²) per check.

## The request algorithm

When process `p` asks for a vector `Request`:

1. If `Request > Need[p]` in any component: error. It has exceeded its declared maximum.
2. If `Request > Available` in any component: `p` must wait; the resources simply aren't there.
3. Otherwise, **pretend to grant it**: `Available −= Request`, `Allocation[p] += Request`, `Need[p] −= Request`.
4. Run the safety algorithm on the pretend state. Safe: make it real. Unsafe: roll back and make `p` wait.

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

Five processes, three resource types. Totals: A = 10, B = 5, C = 7. (This is the standard textbook example from Silberschatz's *Operating System Concepts*.)

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

`Available` is the total minus the column sums of `Allocation`: (10−7, 5−2, 7−5) = (3, 3, 2). `Need` is `Max − Allocation`, row by row.

### Is it safe?

Run the safety algorithm, scanning P0 to P4 each pass:

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

1. Need[P1] = (1, 2, 2). Is (1, 0, 2) ≤ it? Yes.
2. Available = (3, 3, 2). Is (1, 0, 2) ≤ it? Yes.
3. Pretend: Available = (2, 3, 0); Alloc[P1] = (3, 0, 2); Need[P1] = (0, 2, 0).
4. Safety check from Work = (2, 3, 0): P1 needs (0, 2, 0), fits, Work becomes (5, 3, 2). From there, P3, P4, P0, P2 finish exactly as before.

Safe, so **grant**.

### Then P0 requests (0, 2, 0)

1. Need[P0] = (7, 4, 3): fine.
2. Available = (2, 3, 0): fine.
3. Pretend: Available = (2, 1, 0); Need[P0] = (7, 2, 3).
4. Safety check from Work = (2, 1, 0):

```
P0 7 2 3   no (A)
P1 0 2 0   no (B: 2 > 1)
P2 6 0 0   no (A)
P3 0 1 1   no (C: 1 > 0)
P4 4 3 1   no
```

No process can finish. Unsafe, so P0 **waits**, even though two units of B are sitting free.

### And P4 requests (3, 3, 0)

Available is (2, 3, 0) and 3 > 2 for A. Step 2 fails: P4 waits because the resources simply aren't there. No safety check needed.

## Single-instance resources: the claim-edge graph

If every resource has one instance, there's a cheaper variant using the resource-allocation graph. Each process declares in advance which resources it may request; these appear as dashed **claim edges** `P - - > R`. A request turns a claim edge into a request edge, and it's granted only if converting it to an assignment edge `R → P` creates **no cycle** (counting claim edges). A graph traversal detects cycles in O(V + E); a dense adjacency-matrix representation can take O(V²).

## Practical limitations

Using this safety test as a general resource manager requires strong assumptions:

- **Max claims are unknown.** A web server thread has no idea how many locks, buffers or file handles it will need.
- **The population changes.** Processes and threads come and go constantly; new claims must be registered and checked against the safety invariant. A changing population is additional bookkeeping, not a fundamental prohibition.
- **Resources change.** Devices fail and memory gets hot-plugged.
- **It's conservative.** Unsafe isn't deadlocked, so it refuses requests that would have been fine, wasting capacity.
- **It's expensive.** O(m·n²) on every request is a lot with thousands of threads.
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
- The Banker's algorithm needs `Available`, `Max`, `Allocation` and `Need = Max − Allocation`, and costs O(m·n²) per check.
- In the safety check, a finished process gives back its allocation; greedy selection never needs backtracking.
- A request can be refused even when the resources are free, if granting it would make the state unsafe.
- Unknown maximum claims and changing populations complicate direct use; admission control shares the idea of reserving capacity before accepting work.

## Further reading
- [Banker's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Banker%27s_algorithm)
- [Deadlock (computer science): avoidance — Wikipedia](https://en.wikipedia.org/wiki/Deadlock_(computer_science))
- [OSTEP: Common Concurrency Problems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
