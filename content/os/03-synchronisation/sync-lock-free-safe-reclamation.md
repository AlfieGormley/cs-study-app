---
id: sync-lock-free-safe-reclamation
title: Retire nodes before freeing them
level: advanced
minutes: 3
summary: Separate address-reuse ABA from the earlier dereference that may already access freed memory.
sourceLesson: sync-lock-free
---

In a Treiber pop, a thread first loads the atomic top pointer, then reads the node’s next field, then attempts CAS. Another thread must not free or recycle that node between the first two steps.

## Safe memory reclamation

The second bug on the `(!)` line is a **use-after-free**. Between T1 loading `old` and reading `old->next`, T2 may have popped that node and freed it. T1 then reads memory that was already freed, which may crash or return garbage, even if the CAS later fails.

With a sound shared-lock and lifetime protocol, removal/freeing and every relevant dereference are coordinated. A lock protects nothing if some accesses or frees ignore it. Without one, you need a way to know when **no thread can still be looking at a node**. The main schemes are:

| Scheme | Idea |
|---|---|
| Garbage collection | freed only when unreachable |
| Hazard pointers | threads announce what they read |
| Epoch-based | free after all threads move on |
| RCU | free after an RCU grace period |

- **Garbage collection** prevents freeing a node or recycling its address while a live reference remains. It does not prevent logical ABA if the program explicitly removes and reinserts the same node, so node-reuse rules still matter. This removes one reclamation burden in managed runtimes, while logical reuse still needs an algorithmic argument. `java.util.concurrent.ConcurrentLinkedQueue` is based on the **Michael–Scott queue** (1996), which uses CAS on both the head and the tail.
- **Hazard pointers** (Maged Michael, 2004): before dereferencing a node, a thread publishes its address in a per-thread "hazard" slot and re-checks it is still reachable. A thread that wants to free a node first scans everyone's hazard slots and defers the free if it finds a match.
- **Epoch-based reclamation** (used by Rust's `crossbeam-epoch`): threads mark themselves as active in a global epoch; retired nodes are freed once every active thread has moved past the epoch in which they were retired. This can reduce per-access announcement work compared with hazard pointers, but the cost depends on the implementation and workload; one stalled pinned thread can prevent epoch advancement and delay reclamation.

WG21 adopted P2530R3 (hazard pointers) and P2545R4 (RCU) into the C++ working paper at the June 2023 Varna meeting. The proposed hazard_pointer and rcu headers still require an appropriate language/library implementation; check its actual interface and availability before relying on them.

## Key takeaways

- Reading a removed node before CAS can already be a use-after-free.
- Hazard pointers and epoch schemes delay reuse while a reference could remain live.
- A reclamation scheme also needs valid publication and node-reinsertion rules; finite tags alone are insufficient.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [WG21 editor report: June 2023 adopted motions](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4959.html)
