---
id: dl-detection-recovery-whole-retry
title: Retrying the whole transaction safely
level: intermediate
minutes: 3
sourceLesson: dl-detection-recovery
summary: Use a bounded retry loop around the complete logical transaction on an initially idle connection.
---

## Your side: retry the whole transaction

Detection turns a hang into an error. If retrying is appropriate, roll back and rerun the *entire* logical transaction with a retry limit. The example assumes no enclosing transaction or savepoint and no irreversible effects in the retried work.

The pause before each retry grows exponentially but is drawn at random below a cap, so two victims that collided are unlikely to retry at the same instant:

```formula
cap_n = 0.05 s × 2^n
pause_n = U cap_n
cap_3 = 0.05 s × 2^3 = 0.4 s
where
n: the number of failed attempts so far minus one: 0 after the first failure, 1 after the second, and so on
cap_n: the longest pause allowed after failure n + 1, in seconds (s)
U: a random number between 0 and 1, drawn fresh each time (Python's random.random(), which can return 0 but never 1)
pause_n: the actual pause, in seconds, somewhere between 0 and cap_n
cap_3: the ceiling after the fourth failure, the largest one with the default five tries
s: seconds
In words: each failure doubles the ceiling on the wait, starting from 50 ms, and the actual wait is a random fraction of it.
```

So the ceilings run 50 ms, 100 ms, 200 ms and 400 ms, and with the default `tries=5` there are at most four pauses. On average a pause is half its ceiling. In the code below, `n` is the loop counter, `cap` is cap_n and `pause` is pause_n:

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
            # Own one complete transaction
            # attempt.
            with conn.transaction():
                return work(conn)
        except RETRY:
            if n + 1 == tries:
                raise
            cap = 0.05 * 2 ** n
            pause = cap * random.random()
            # Rollback has already left the
            # context.
            time.sleep(pause)
```

Use a dedicated connection, initially idle (for example, an autocommit connection). `work` must not commit or roll back explicitly. Each context then owns a whole transaction, rolls back on error, and commits on successful exit. Jitter reduces repeated collisions; it does not guarantee progress.

Pitfalls:

- **Side effects outside the database.** If `work` sends an email or calls a payment API, a retry does it twice. Do those after commit, or make them idempotent.
- **Retrying only the statement.** After a deadlock error the transaction is aborted; further statements fail until you roll back.
- **Retrying forever.** Opposite lock ordering can repeatedly deadlock when operations overlap, even if some retries succeed. Retries hide it; lock ordering fixes it.

## Key takeaways
- Use a bounded retry loop around the complete logical transaction on an initially idle connection.
- The context manager rolls back a failed attempt before the next begins.
- Jitter reduces collisions; external side effects require idempotency or reliable post-commit handling.

## Further reading
- [Psycopg 3: transaction contexts](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)
- [PostgreSQL: explicit locking and deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
- [AWS: exponential back-off and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
