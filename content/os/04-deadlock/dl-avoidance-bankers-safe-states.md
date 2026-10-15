---
id: dl-avoidance-bankers-safe-states
title: Safe states and the cautious banker
level: intermediate
minutes: 3
sourceLesson: dl-avoidance-bankers
summary: A safe sequence guarantees completion under declared maximum claims and eventual release.
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

## Key takeaways
- A safe sequence guarantees completion under declared maximum claims and eventual release.
- Unsafe does not mean already deadlocked: actual future requests may be smaller.
- A request for currently free units can make a state unsafe.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
