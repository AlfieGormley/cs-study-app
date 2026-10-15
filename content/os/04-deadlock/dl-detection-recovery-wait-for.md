---
id: dl-detection-recovery-wait-for
title: Detecting cycles with a wait-for graph
level: intermediate
minutes: 3
sourceLesson: dl-detection-recovery
summary: Collapse exclusive resource nodes to edges between waiting processes and holders.
---

Prevention restricts how you write code. Avoidance needs every process to declare its maximum claim. Their costs and the frequency of deadlocks depend on the workload.

**Detection and recovery** takes the optimistic view: let threads and transactions request whatever they like, check now and then for a deadlock, and when one turns up, break it by force. PostgreSQL, InnoDB and SQL Server support this approach.

## When detection is the right call

Detection makes sense when three things are true:

- Deadlocks are **rare**, so the occasional recovery is cheaper than constant prevention.
- You **can't control the lock order**. Arbitrary SQL can discover rows in different orders; imposing one global order on every transaction is restrictive. Applications can still deliberately use consistent lock ordering.
- Recovery is **supported and affordable for the workload**. Transactional database changes can be rolled back; rollback may be expensive, and external effects need separate handling.

The third point is why operating systems rarely do this for user-space locks. Killing a thread that holds a mutex leaves the data it was protecting half-updated, and there's no undo log. Databases have one.

## Single-instance resources: the wait-for graph

In the classical model of indefinitely blocking, exclusive single-instance resources (such as an exclusive mutex), take the resource-allocation graph from the deadlock fundamentals lessons and collapse out the resource nodes. If T1 is waiting for a lock held by T2, draw an edge `T1 → T2`. This is the **wait-for graph**.

```
Resource-allocation graph:

  T1 --req--> R1 --held--> T2
  T2 --req--> R2 --held--> T3
  T3 --req--> R3 --held--> T1

Wait-for graph:

     T1 -----> T2
      ^         |
      |         v
      +-------- T3
```

With single-instance resources, **a cycle in the wait-for graph is a deadlock**, and every deadlock is a cycle. So detection is just cycle detection, which a depth-first search (DFS) does in O(V + E), where V is the number of vertices (here, waiting or holding transactions) and E the number of wait-for edges.

```python
def find_cycle(waits_for):
    # waits_for: {txn: set of txns}
    GREY, BLACK = 1, 2
    colour = {}
    path = []

    def dfs(t):
        colour[t] = GREY
        path.append(t)
        for u in waits_for.get(t, ()):
            c = colour.get(u)
            if c == GREY:      # back edge
                i = path.index(u)
                # Return the cycle, not its
                # tail.
                return path[i:]
            if c is None:
                cyc = dfs(u)
                if cyc:
                    return cyc
        path.pop()
        # Completed paths need no second
        # search.
        colour[t] = BLACK
        return None

    for t in list(waits_for):
        if t not in colour:
            cyc = dfs(t)
            if cyc:
                return cyc
    return None
```

A **grey** node is on the current DFS path; meeting one again means you've come back round to where you started, which is a cycle. A **black** node has been fully explored without finding a cycle, so it's skipped.

```python
g = {"T1": {"T2"}, "T2": {"T3"},
     "T3": {"T1"}, "T4": {"T1"}}
print(find_cycle(g))
# ['T1', 'T2', 'T3']
```

T4 is waiting on the cycle but isn't part of it. It's stuck, but it isn't the cause: aborting T4 would not release the locks blocking this cycle. Recovery has to pick a victim from inside the cycle.

## Key takeaways
- Collapse exclusive resource nodes to edges between waiting processes and holders.
- DFS distinguishes a current-traversal back edge from an already explored node.
- Recovery must remove a participant in the cycle, rather than an unrelated waiter.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [PostgreSQL: explicit locking and deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
