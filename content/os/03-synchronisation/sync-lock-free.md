---
id: sync-lock-free
title: Lock-free structures, RCU and read-write locks
level: advanced
minutes: 17
summary: Progress guarantees, CAS retry loops and the Treiber stack, the ABA problem and safe memory reclamation, and the read-mostly toolkit of read-write locks, seqlocks and RCU.
---

Locks are simple and correct, but they have one structural weakness: **if the thread holding a lock stops, everyone waiting for it stops too**. The holder might be preempted, page-faulting, running a signal handler, or simply slow. Under heavy load that one stalled thread sets the pace for all the others.

Lock-free techniques avoid holding anything that others must wait for. Instead of "acquire, modify, release", threads prepare a change privately and publish it with a single atomic instruction, retrying if someone else got there first. This lesson covers how that works, why it is much harder than it looks, and the more practical read-mostly tools (read-write locks, seqlocks and RCU) that real kernels and servers rely on.

## Progress guarantees

"Lock-free" has a precise meaning. It describes what happens when threads are delayed, not whether the code contains the word `lock`.

| Guarantee | Promise |
|---|---|
| Blocking | a stalled thread can stop all |
| Obstruction-free | a thread alone finishes |
| Lock-free | some thread always progresses |
| Wait-free | every thread finishes, bounded |

- **Blocking**: any algorithm using a mutex. If the holder is descheduled, nobody else in that critical section progresses.
- **Obstruction-free**: a thread finishes in a bounded number of steps if all others pause. Contending threads may keep undoing each other's work.
- **Lock-free**: continued execution guarantees system-wide operation progress under the algorithm's primitive and scheduling assumptions. An individual operation can starve; this is not a fixed wall-clock completion deadline.
- **Wait-free**: *every* thread completes in a bounded number of its own steps, however others behave. The strongest guarantee and the hardest to build.

A spinlock built from CAS is **not** lock-free: if the holder is preempted, every spinner makes zero progress. Using atomic instructions does not by itself make an algorithm lock-free.

Maurice Herlihy showed in 1991 that primitives differ in power. Plain loads and stores, or test-and-set, cannot build wait-free versions of every data structure for arbitrary numbers of threads; compare-and-swap (and LL/SC) can. That is why CAS is the foundation of everything in this lesson.

## The CAS retry loop

The basic lock-free pattern is: read the current value, compute a new one privately, and CAS it in. If the CAS fails, someone else changed the value first, so start again.

```c
#include <stdatomic.h>

atomic_long max_seen = 0;

void record(long v) {
    long cur = atomic_load(&max_seen);
    while (v > cur &&
           !atomic_compare_exchange_weak(
               &max_seen, &cur, v))
        ;  // cur now holds the new value
}
```

On failure, C11's CAS writes the value it found into `cur`, so the loop re-tests with fresh data. Assuming `atomic_long` is lock-free on the target implementation, the loop has system-wide non-blocking progress: apart from the occasional spurious failure that `_weak` allows, a CAS only fails because another thread's update *succeeded*, so every failure means someone else made progress.

CAS retry loops generally do not give each thread a fixed retry bound. By contrast, a fetch-add implemented as one native instruction has a bounded number of algorithmic steps, assuming that primitive completes. This is not a bound on wall-clock latency: scheduling, faults and hardware contention still matter.

## A lock-free stack

The **Treiber stack** (R. Kent Treiber, IBM, 1986) is the "hello world" of lock-free structures. The stack is a linked list, and `top` is an atomic pointer.

```c
struct node {
    int val;
    struct node *next;
};

_Atomic(struct node *) top = NULL;

void push(struct node *n) {
    struct node *old = atomic_load(&top);
    do {
        n->next = old;
    } while (!atomic_compare_exchange_weak(
                 &top, &old, n));
}
```

Push links the new node to the current top, then tries to swing `top` to it. If another thread pushed or popped in between, `top` no longer equals `old`, the CAS fails, `old` is refreshed and we relink.

```c
struct node *pop(void) {
    struct node *old, *next;
    old = atomic_load(&top);
    do {
        if (old == NULL)
            return NULL;
        next = old->next;   // (!)
    } while (!atomic_compare_exchange_weak(
                 &top, &old, next));
    return old;
}
```

Garbage collection helps with reclamation, but the algorithm still needs correct atomic publication and must prevent unsafe node reinsertion. In C it has two serious bugs, both hiding on the line marked `(!)`.

## The ABA problem

CAS asks "is `top` still equal to `old`?". It cannot tell whether `top` **changed and then changed back**. That is the **ABA problem**.

Start with the stack `A → B → C`.

```
T1: pop: old = A, next = B
    ... T1 is preempted ...
T2: pop()        -> A    top = B
T2: pop()        -> B    top = C
T2: free(B)
T2: push(A)  (reuses A) top = A -> C
    ... T1 resumes ...
T1: CAS(top, A, B)  succeeds!
                         top = B (freed)
```

T1's CAS succeeds because `top` is A again, but the A it sees is a *different moment* of A, and the `next` it computed (B) is stale. The stack now points at freed memory, and C has been lost. A memory allocator recycling a freed node's address causes exactly the same thing, so you do not need to push the "same" node deliberately.

The fixes:

1. **Tagged pointers.** Pair the pointer with a version counter and CAS both together. Every successful update increments the counter, so "A, version 7" no longer matches "A, version 9". x86-64 offers a 16-byte CAS (`cmpxchg16b`) for pointer-plus-counter pairs; packing a small counter into pointer bits is platform-specific and requires validating address representation and atomic support. A 16-bit tag wraps after 65536 updates; any finite tag needs an argument that wraparound cannot alias an outstanding observation.
2. **LL/SC.** ARM's load-linked/store-conditional fails if the location was written *at all* since the load, so in principle it is immune. In practice C11's `compare_exchange` on ARM still compares values, so C code gets the ABA problem anyway.
3. **Do not reuse memory while anyone might hold a reference.** This is the real fix, and it leads to the next problem.

## Safe memory reclamation

The second bug on the `(!)` line is a **use-after-free**. Between T1 loading `old` and reading `old->next`, T2 may have popped that node and freed it. T1 then reads freed memory, which may crash or return garbage, even if the CAS later fails.

With a lock this cannot happen: nobody frees a node while someone else is inside the critical section. Without one, you need a way to know when **no thread can still be looking at a node**. The main schemes are:

| Scheme | Idea |
|---|---|
| Garbage collection | freed only when unreachable |
| Hazard pointers | threads announce what they read |
| Epoch-based | free after all threads move on |
| RCU | free after a grace period |

- **Garbage collection** prevents freeing a node or recycling its address while a live reference remains. It does not prevent logical ABA if the program explicitly removes and reinserts the same node, so node-reuse rules still matter. That is why lock-free structures are far more common in Java and Go. `java.util.concurrent.ConcurrentLinkedQueue` is based on the **Michael–Scott queue** (1996), which uses CAS on both the head and the tail.
- **Hazard pointers** (Maged Michael, 2004): before dereferencing a node, a thread publishes its address in a per-thread "hazard" slot and re-checks it is still reachable. A thread that wants to free a node first scans everyone's hazard slots and defers the free if it finds a match.
- **Epoch-based reclamation** (used by Rust's `crossbeam-epoch`): threads mark themselves as active in a global epoch; retired nodes are freed once every active thread has moved past the epoch in which they were retired. Cheaper per access than hazard pointers, but one stalled thread can stop all reclamation.

WG21 proposals P2530 and P2545 specify hazard-pointer and RCU facilities for C++; check the chosen standard-library implementation before relying on availability.

## Read-write locks

Many shared structures are read far more often than written: routing tables, configuration, caches, DNS zones. A **read-write lock** lets any number of readers in at once and gives writers exclusive access.

```c
pthread_rwlock_t rw =
    PTHREAD_RWLOCK_INITIALIZER;

int lookup(int key) {
    pthread_rwlock_rdlock(&rw);
    int v = table_get(key);
    pthread_rwlock_unlock(&rw);
    return v;
}

void update(int key, int v) {
    pthread_rwlock_wrlock(&rw);
    table_put(key, v);
    pthread_rwlock_unlock(&rw);
}
```

It seems like an obvious win, but it often disappoints:

- **Readers still write.** Each `rdlock` and `unlock` is an atomic update to the shared reader count. With 32 cores doing short lookups, that one cache line bounces between cores just as a mutex's would. For sufficiently short reads, this overhead can outweigh reader parallelism; there is no universal duration threshold.
- **Starvation.** As in the readers–writers problem, a reader-preferring lock (glibc's default) can starve writers; a writer-preferring one can starve readers.
- **Upgrade deadlock.** Two readers that each try to upgrade to a write lock wait for each other to stop reading. Most libraries do not support upgrading for this reason.

Longer read sections and rare writes can make reader parallelism worthwhile, but the crossover must be measured on the actual implementation and hardware. For short, very hot reads you want readers that write nothing shared at all.

## Seqlocks

A **seqlock** lets readers proceed without writing anything. The writer increments a sequence counter before and after each update, so the counter is odd while a write is in progress. Readers read the counter, read the data, then read the counter again, and retry if it was odd or has changed.

```
writer (writers serialised by a lock):
  seq++            // now odd
  write data
  seq++            // even again

reader:
  do {
    s = seq        // wait while odd
    copy data
  } while (s is odd || seq != s)
```

This is algorithm pseudocode. Portable C requires a race-free representation (for example atomic fields) plus a proven ordering protocol; retrying does not undo undefined behavior. Linux seqlock APIs follow the Linux kernel memory model and do not magically make arbitrary plain C fields portable atomic objects. Writers must also meet the API's serialization and non-preemption requirements.

These readers do not take the writer lock or update a shared reader count, reducing contention. They do not scale perfectly: cache traffic and repeated retries still cost time. The cost: a reader may read torn, inconsistent data and must throw it away and retry, so it must not follow pointers inside that data (they might point to freed memory). Seqlocks suit small, plain values updated often and read constantly. Linux uses them for timekeeping, where the current time is read by every `clock_gettime` call and updated on every timer tick.

## RCU: read-copy-update

**RCU** gives readers the same near-zero cost, but for linked, pointer-based data. It has been used throughout the Linux kernel since 2002 (Paul McKenney and others), for routing tables, the directory-entry cache, module lists and much more.

The idea is in the name. In this immutable-configuration example, a writer does not modify a published object. Instead it:

1. **Reads** the current version.
2. **Copies** it and modifies the copy.
3. **Updates** a shared pointer to the new version with a single release store (publication).
4. Waits for a **grace period**: until every reader that might still be using the old version has finished.
5. Frees the old version.

```c
struct config *cur;   // RCU-protected

int get_timeout(void) {
    rcu_read_lock();
    struct config *c =
        rcu_dereference(cur);
    int t = c->timeout;
    rcu_read_unlock();
    return t;
}

void set_timeout(int t) {   // under a mutex
    struct config *old = cur;
    struct config *new =
        malloc(sizeof *new);
    if (!new) return;  // report failure
    *new = *old;
    new->timeout = t;
    rcu_assign_pointer(cur, new);
    synchronize_rcu();   // grace period
    free(old);
}
```

This is RCU-style pseudocode: a real kernel implementation uses kernel allocation and protected pointer-access APIs; a liburcu application needs its selected flavor's headers, registration and lifecycle rules. Assume cur initially refers to a valid object and writers hold the same mutex.

`rcu_assign_pointer` is a release store and `rcu_dereference` an ordered load, so a reader that sees the new pointer also sees the fully built object. That is the double-checked-locking lesson again.

```
time ---------------------------------->
R1  [--- reads old ---]
R2      [--- reads old ---]
pub         ^ new pointer published
R3              [-- reads new --]
GP          |<-- grace period -->|
free                             ^ old
```

synchronize_rcu waits for read-side sections that pre-exist its invocation, not necessarily every later reader. In the simplified diagram publication and the start of the grace-period wait are adjacent; R1/R2 may retain the old object. Actual grace-period completion need not coincide with the last illustrated unlock.

How does the kernel know when a grace period has ended without readers announcing themselves? In a non-preemptible kernel, an RCU reader may not sleep or be preempted, so once **every CPU has passed through a context switch**, no pre-existing reader can still be running. `rcu_read_lock()` then compiles to little or nothing. Costs and grace-period duration depend on RCU flavor, configuration and workload; no fixed timing is supplied here. `call_rcu()` lets a writer register a callback to free the old data later instead of blocking.

The trade-offs:

- Readers may see **slightly stale** data for a moment after an update. Fine for a routing table; wrong for a bank balance.
- Writers are slow and must serialise among themselves (usually with an ordinary mutex).
- Old versions stay in memory until their grace period ends, so a burst of updates can raise memory use.

In user space, `liburcu` provides RCU for applications.

### The same idea in Python

Managed runtimes help keep referenced objects alive, but do not supply publication ordering or application immutability automatically. This example uses a brief shared lock to obtain or publish a snapshot, then allows use of that immutable snapshot outside the lock.

```python
import threading

_config = {"timeout": 10}  # never mutated
_write_lock = threading.Lock()

def get_config():
    with _write_lock:
        return _config  # immutable snapshot

def set_timeout(t):
    global _config
    with _write_lock:      # publish lock
        new = dict(_config)
        new["timeout"] = t
        _config = new      # publish
```

Readers briefly take the publication lock, then retain a reference to an unchanged dictionary. Reclamation timing is runtime-dependent. Callers must not mutate the returned dictionary or mutable objects reachable from it. Java's `CopyOnWriteArrayList` is the same pattern for lists: every write copies the array, so it only suits collections that are read far more than written.

The rule that makes this safe: **never mutate a published object**. `_config["timeout"] = 30` could violate the snapshot invariant; do not equate Python compound-operation races with the precise C data-race definition.

> [!note] Content gap
> No hardware-specific lock, cache-transfer or RCU timing benchmark is available. The stack deliberately omits safe reclamation, and the seqlock/RCU fragments are protocol illustrations, not complete production implementations.

## Choosing a tool

| Situation | Reach for |
|---|---|
| Shared counter | atomic fetch-add |
| Small, hot, plain data | seqlock |
| Read-mostly linked data | RCU or copy-on-write |
| Long reads, some writes | read-write lock |
| Queue between threads | library queue |
| Anything else | a mutex |

> [!warning] Lock-free is not automatically faster
> Under heavy contention on one word, CAS loops fail and retry repeatedly, and the cache line still bounces between cores. A well-implemented mutex that puts waiters to sleep can beat a naive lock-free structure. Lock-free code is also very hard to get right and test. Use proven libraries (`java.util.concurrent`, Rust's `crossbeam`, Folly, Boost.Lockfree, `liburcu`) and benchmark before replacing a lock.

## Key takeaways
- Lock-free means some thread always makes progress even if others stall; wait-free means every thread does. A CAS-based spinlock is neither.
- The core pattern is read, compute privately, CAS, retry on failure. A non-spurious CAS failure indicates interference; weak CAS may also fail spuriously.
- CAS cannot detect a value that changed and changed back (ABA). Tagged pointers help, but the real fix is safe memory reclamation: garbage collection, hazard pointers, epochs or RCU.
- Read-write-lock benefits depend on workload; short reads may contend on shared reader metadata. Seqlocks and RCU let readers write nothing shared.
- RCU publishes a new copy with a release store and frees the old one after a grace period, making reads nearly free at the cost of slower writers and briefly stale reads. Copy-on-write with an immutable object is the same idea in Python and Java.

## Further reading
- [Non-blocking algorithm — Wikipedia](https://en.wikipedia.org/wiki/Non-blocking_algorithm)
- [ABA problem — Wikipedia](https://en.wikipedia.org/wiki/ABA_problem)
- [Treiber stack — Wikipedia](https://en.wikipedia.org/wiki/Treiber_stack)
- [Simple, fast, and practical non-blocking concurrent queues — Michael and Scott (PDF)](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Hazard pointer — Wikipedia](https://en.wikipedia.org/wiki/Hazard_pointer)
- [What is RCU, fundamentally? — LWN](https://lwn.net/Articles/262464/)
- [What is RCU? — Linux kernel documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Sequence counters and sequential locks — Linux kernel documentation](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU (liburcu)](https://liburcu.org/)
