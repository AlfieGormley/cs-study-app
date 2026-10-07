---
id: dl-detection-recovery
title: Detection and recovery
level: intermediate
minutes: 13
summary: Letting deadlocks happen, finding them with wait-for graphs and the multi-instance detection algorithm, breaking them by choosing a victim, and how PostgreSQL, MySQL and SQL Server do it.
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

In the classical model of indefinitely blocking, exclusive single-instance resources (such as an exclusive mutex), take the resource-allocation graph from lesson 1 and collapse out the resource nodes. If T1 is waiting for a lock held by T2, draw an edge `T1 → T2`. This is the **wait-for graph**.

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

With single-instance resources, **a cycle in the wait-for graph is a deadlock**, and every deadlock is a cycle. So detection is just cycle detection, which a depth-first search does in O(V + E).

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
                return path[i:]
            if c is None:
                cyc = dfs(u)
                if cyc:
                    return cyc
        path.pop()
        colour[t] = BLACK
        return None

    for t in list(waits_for):
        if t not in colour:
            cyc = dfs(t)
            if cyc:
                return cyc
    return None
```

A **grey** node is on the current DFS path; meeting one again means you've come back round to where you started, which is a cycle. A **black** node has been fully explored and is known not to lead to a cycle, so it's skipped.

```python
g = {"T1": {"T2"}, "T2": {"T3"},
     "T3": {"T1"}, "T4": {"T1"}}
print(find_cycle(g))
# ['T1', 'T2', 'T3']
```

T4 is waiting on the cycle but isn't part of it. It's stuck, but it isn't the cause: aborting T4 would not release the locks blocking this cycle. Recovery has to pick a victim from inside the cycle.

## Multiple instances: the detection algorithm

With several units per resource type, a cycle is no longer proof (lesson 1). The test instead looks like the Banker's safety check, with two changes:

1. Compare each process's **current request**, not its maximum `Need`. Detection asks "can everyone finish given what they're asking for right now?", not "in the worst case".
2. A process holding no units cannot sustain a resource deadlock in this model, so mark it finished. It may still be blocked behind the deadlocked holders.

```python
def deadlocked(avail, alloc, request):
    # Nonnegative, matching shapes.
    n = len(alloc)
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
                    work[k] += alloc[i][k]
                done[i] = True
                progress = True
    return [i for i in range(n)
            if not done[i]]
```

The optimistic step is "assume a process whose request fits will finish and release everything". If it later asks for more, the next detection run will catch any problem.

### Worked example

Five processes, totals A = 7, B = 2, C = 6 (another Silberschatz example):

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

Nothing is free, which looks alarming. Run the algorithm:

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

Now P2 asks for one more C, so `Request[P2] = (0, 0, 1)`. Rerun: P0 finishes, giving Work = (0, 1, 0). Now P1 needs A, P2 needs C, P3 needs A and P4 needs C, and Work has neither. **P1, P2, P3 and P4 are deadlocked.**

## How often to look

Detection costs O(V + E) for the graph, or O(m·n²) for the matrix version. You choose when to pay:

| Trigger | Trade-off |
|---|---|
| On every lock wait | Prompt checks; cost grows with waits |
| After waiting `t` seconds | Delay before checking that waiter |
| Periodically | Cost bounded; many cycles may pile up |
| When throughput drops | Cheap; vague signal |

A delayed check avoids work for waits that resolve before its timer. Detection policy and useful delay depend on the engine and workload.

## Recovery: breaking the cycle

Once you've found a cycle, someone has to give something up. There are two broad options.

**Abort processes.** Either abort every member of the cycle (simple, wasteful) or abort one at a time and rerun detection until the cycle is gone. Aborting one can discard less work, which raises the question of *which* one.

**Preempt resources.** Take a resource from a victim, roll the victim back to a point before it acquired it, and restart it from there. This needs **checkpoints** or an undo log. Database recovery mechanisms can undo or invalidate a victim's transactional changes before releasing its transaction-scoped locks. The details differ: PostgreSQL uses MVCC tuple visibility rather than a general InnoDB-style undo log, and session-scoped locks need not be released by transaction rollback.

### Choosing a victim

Possible criteria (engine policies differ):

1. **Explicit priority**, if the user set one.
2. **Cost of rollback**: how much work would be thrown away (rows changed, log written, CPU used).
3. **Locks held**: aborting a transaction with many locks may unblock more waiters.
4. **How many times it has already been a victim.**

The last one prevents **starvation**. If the cheapest transaction is always chosen, a small transaction that keeps colliding with big ones can be rolled back forever. Increasing protection for repeated victims can mitigate this. A starvation-freedom guarantee also needs fair scheduling, finite transactions and a policy that eventually protects each retry.

## Databases in practice

These three engines detect deadlocks, but they differ in when they look and whom they kill.

**PostgreSQL** doesn't check on every wait. A backend that has been waiting for a lock for `deadlock_timeout` (default 1 s) runs the check itself, walking the wait-for graph from its own transaction. If it finds a cycle, it normally aborts its own transaction with `ERROR: deadlock detected` (SQLSTATE `40P01`). The docs warn that which transaction gets aborted is hard to predict and shouldn't be relied on. The log message lists each process, what it waited for and who blocked it.

**MySQL InnoDB** enables detection by default through `innodb_deadlock_detect`. In the MySQL 8.4 source, wait-graph changes wake a detector thread; detection is not a zero-delay synchronous guarantee. It tries to roll back the **smallest** transaction, measured by the number of rows inserted, updated or deleted, and returns error 1213. On very high-concurrency systems the check itself can become a bottleneck, so some operators turn it off and rely on `innodb_lock_wait_timeout` (default 50 s) instead.

**SQL Server** runs a background lock monitor that searches every 5 seconds by default, dropping to as little as 100 ms while it keeps finding deadlocks. The victim is the session with the lowest `DEADLOCK_PRIORITY`; on a tie, the transaction that is cheapest to roll back. The victim gets error 1205.

> [!note] Timeouts are a cruder detector
> A lock timeout ends an overlong wait without proving a cycle. PostgreSQL marks the current transaction or subtransaction failed. InnoDB normally rolls back only the timed-out statement, leaving the transaction and earlier locks active; explicitly roll back the transaction when abandoning/retrying the whole unit. Merely timing out a statement does not guarantee that every held lock is released. A timeout cannot distinguish deadlock from a slow holder.

## Your side: retry the whole transaction

Detection turns a hang into an error. If retrying is appropriate, roll back and rerun the *entire* logical transaction with a retry limit. The example assumes no enclosing transaction or savepoint and no irreversible effects in the retried work.

```python
import random
import time
from psycopg import errors
from psycopg.pq import TransactionStatus

RETRY = (errors.DeadlockDetected,
         errors.SerializationFailure)

def run_txn(conn, work, tries=5):
    if conn.info.transaction_status != (
        TransactionStatus.IDLE
    ):
        raise ValueError("idle connection")
    if tries < 1:
        raise ValueError("tries > 0")
    for n in range(tries):
        try:
            with conn.transaction():
                return work(conn)
        except RETRY:
            if n + 1 == tries:
                raise
            cap = 0.05 * 2 ** n
            pause = cap * random.random()
            time.sleep(pause)
```

Use a dedicated connection, initially idle (for example, an autocommit connection). `work` must not commit or roll back explicitly. Each context then owns a whole transaction, rolls back on error, and commits on successful exit. Jitter reduces repeated collisions; it does not guarantee progress.

Pitfalls:

- **Side effects outside the database.** If `work` sends an email or calls a payment API, a retry does it twice. Do those after commit, or make them idempotent.
- **Retrying only the statement.** After a deadlock error the transaction is aborted; further statements fail until you roll back.
- **Retrying forever.** Opposite lock ordering can repeatedly deadlock when operations overlap, even if some retries succeed. Retries hide it; lock ordering fixes it.

## Prevention inside the database: wait-die and wound-wait

Some databases, especially distributed ones where building a global wait-for graph is hard, prevent deadlock instead, using transaction **timestamps** (older = smaller). When transaction Ti requests a lock held by Tj:

| Scheme | Ti older than Tj | Ti younger than Tj |
|---|---|---|
| Wait-die | Ti waits | Ti aborts ("dies") |
| Wound-wait | Tj aborts ("wounded") | Ti waits |

In both, waits only ever go in one direction of age (younger waits for older, or the reverse), so no cycle can form. An aborted transaction restarts with its **original** timestamp, so newer arrivals do not continually jump ahead. Eventual completion also assumes older transactions finish and scheduling/retries are fair.

Google's Spanner uses wound-wait for its read-write transactions. The trade-off is that both schemes abort some transactions that would never have deadlocked, just because they were the wrong age.

## Key takeaways
- Detection lets deadlocks happen and breaks them afterwards; it suits systems where deadlocks are rare and rollback is cheap, like databases.
- With single-instance resources, a cycle in the wait-for graph is exactly a deadlock, found by DFS in O(V + E).
- With multiple instances, run a Banker's-style check against current requests; processes left unfinished are deadlocked.
- Recovery aborts or preempts a victim from inside the cycle, chosen by priority and rollback cost; count prior aborts to avoid starving one transaction.
- PostgreSQL uses `deadlock_timeout` (default 1 s); InnoDB enables detection by default; SQL Server adapts its default 5 s checking interval. Victim rollback breaks detected cycles.
- When retrying, restart the whole logical transaction with bounded back-off and safe handling of external effects.
- Wait-die and wound-wait use timestamps to prevent deadlock without a wait-for graph, at the cost of extra aborts.

## Further reading
- [PostgreSQL docs: Explicit Locking (deadlocks)](https://www.postgresql.org/docs/current/explicit-locking.html)
- [PostgreSQL docs: Lock Management settings](https://www.postgresql.org/docs/current/runtime-config-locks.html)
- [SQL Server: Deadlocks guide — Microsoft Learn](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide)
- [Wait-for graph — Wikipedia](https://en.wikipedia.org/wiki/Wait-for_graph)
- [Wait-die and wound-wait (Deadlock prevention algorithms) — Wikipedia](https://en.wikipedia.org/wiki/Deadlock_prevention_algorithms)
- [Spanner: Google's Globally-Distributed Database (PDF)](https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf)
