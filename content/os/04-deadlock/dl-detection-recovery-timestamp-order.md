---
id: dl-detection-recovery-timestamp-order
title: Preventing cycles with transaction age
level: intermediate
minutes: 1
sourceLesson: dl-detection-recovery
summary: Wait-die allows only older requesters to wait; wound-wait allows only younger requesters to wait.
---

## Prevention inside the database: wait-die and wound-wait

Some databases, especially distributed ones where building a global wait-for graph is hard, prevent deadlock instead, using transaction **timestamps**: each transaction gets one when it starts, so an older transaction has a smaller timestamp. When transaction Ti requests a lock held by Tj:

| Scheme | Ti older than Tj | Ti younger than Tj |
|---|---|---|
| Wait-die | Ti waits | Ti aborts ("dies") |
| Wound-wait | Tj aborts ("wounded") | Ti waits |

In both, waits only ever go in one direction of age (younger waits for older, or the reverse), so no cycle can form. An aborted transaction restarts with its **original** timestamp, so newer arrivals do not continually jump ahead. Eventual completion also assumes older transactions finish and scheduling/retries are fair.

Google's Spanner uses wound-wait for its read-write transactions. The trade-off is that both schemes abort some transactions that would never have deadlocked, just because they were the wrong age.

## Key takeaways
- Wait-die allows only older requesters to wait; wound-wait allows only younger requesters to wait.
- An aborted transaction retains its original timestamp on retry.
- Fair execution and eventual release are still needed for completion.

## Further reading
- [Linux: wound/wait mutex design](https://docs.kernel.org/locking/ww-mutex-design.html)
- [Spanner: transaction concurrency control](https://cloud.google.com/spanner/docs/transactions)
