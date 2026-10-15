---
id: dl-detection-recovery-victim-policy
title: Choosing detection timing and recovery victims
level: intermediate
minutes: 2
sourceLesson: dl-detection-recovery
summary: Detection frequency trades overhead against the time operations remain blocked.
---

## How often to look

Detection costs O(V + E) for the graph (V transactions, E wait-for edges), or O(m·n²) for the matrix version (n processes, m resource types). You choose when to pay:

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

**Preempt resources.** Take a resource from a victim, roll the victim back to a point before it acquired it, and restart it from there. This needs saved **process checkpoints** or an undo log. Database recovery mechanisms can undo or invalidate a victim's transactional changes before releasing its transaction-scoped locks. The details differ: PostgreSQL uses MVCC tuple visibility rather than a general InnoDB-style undo log, and session-scoped locks need not be released by transaction rollback.

### Choosing a victim

Possible criteria (engine policies differ):

1. **Explicit priority**, if the user set one.
2. **Cost of rollback**: how much work would be thrown away (rows changed, log written, CPU used).
3. **Locks held**: aborting a transaction with many locks may unblock more waiters.
4. **How many times it has already been a victim.**

The last one prevents **starvation**. If the cheapest transaction is always chosen, a small transaction that keeps colliding with big ones can be rolled back forever. Increasing protection for repeated victims can mitigate this. A starvation-freedom guarantee also needs fair scheduling, finite transactions and a policy that eventually protects each retry.

## Key takeaways
- Detection frequency trades overhead against the time operations remain blocked.
- Rollback needs a valid recovery mechanism; arbitrarily killing a lock holder risks corrupt state.
- Repeatedly choosing the cheapest victim can starve it without a protective policy.

## Further reading
- [PostgreSQL: explicit locking and deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
- [SQL Server: deadlock detection and victims](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide)
