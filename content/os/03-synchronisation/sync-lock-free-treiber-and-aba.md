---
id: sync-lock-free-treiber-and-aba
title: Treiber stack and the ABA trap
level: advanced
minutes: 4
summary: Trace pointer publication and an old next pointer that survives a changed-then-restored top.
sourceLesson: sync-lock-free
---

A Treiber stack is a useful algorithm sketch, but the bare C fragments below omit a complete memory-reclamation protocol. Retain node lifetimes and prevent node reuse when experimenting with its pointer-update logic.

## A lock-free stack

The **Treiber stack** (R. Kent Treiber, IBM, 1986) is the "hello world" of lock-free structures. The Treiber stack is a linked list, and `top` is an atomic pointer.

```c
struct node {
    int val;
    struct node *next;
};

_Atomic(struct node *) top = NULL;

void push(struct node *n) {
    struct node *old = atomic_load(&top);
    do {
        // Prepare a private, unpublished
        // link.
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
        // Unsafe unless node lifetime is
        // held.
        next = old->next;   // (!)
    } while (!atomic_compare_exchange_weak(
                 &top, &old, next));
    return old;
}
```

Garbage collection helps with lifetime reclamation, but atomic publication and node-reinsertion rules still matter. In bare C the marked dereference can access freed memory. Separately, a later CAS can install a stale next pointer after an ABA cycle.

## The ABA problem

CAS asks "is `top` still equal to `old`?". It cannot tell whether `top` **changed and then changed back**. That is the **ABA problem**.

Start with the Treiber stack `A → B → C`.

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

T1's CAS succeeds because `top` is A again, but the A it sees is a *different moment* of A, and the `next` it computed (B) is stale. The Treiber stack now points at memory that was already freed, and C is no longer reachable from top through a valid chain. A memory allocator recycling a freed node's address causes exactly the same thing, so you do not need to push the "same" node deliberately.

The fixes:

1. **Tagged pointers.** Pair the pointer with a version counter and CAS both together. Every successful update increments the counter, so "A, version 7" no longer matches "A, version 9". x86-64 offers a 16-byte CAS (`cmpxchg16b`) for pointer-plus-counter pairs; packing a small counter into pointer bits is platform-specific and requires validating address representation and atomic support.

A tag with a fixed number of bits eventually wraps around to a value it has held before:

```formula
U_wrap = 2^b
U_wrap = 2^16 = 65536
where
U_wrap: the number of successful updates after which the tag is back at its starting value
b: the number of bits in the tag; 16 in the example line
2^b: 2 raised to the power b, meaning b copies of 2 multiplied together
In words: each extra tag bit doubles the number of updates before the tag repeats.
```

So a 16-bit tag repeats after 65,536 updates, and a thread stalled across exactly 65,536 updates (or any multiple of it) would see a matching tag and could still be fooled. Any finite tag needs an argument that wraparound cannot alias an outstanding observation.

2. **LL/SC.** A genuine load-linked/store-conditional protocol validates an exclusive reservation rather than only comparing values, so an intervening write can invalidate it even if the value returns. Reservations may fail for other reasons too. C11 compare-exchange still exposes value comparison, even when implemented with LL/SC; it does not acquire an automatic ABA guarantee.
3. **Do not reuse memory while anyone might hold a reference.** This is the real fix, and it leads to the next problem.

## Key takeaways

- A Treiber push or pop publishes its change through compare-exchange.
- Value equality cannot reveal an intervening change and return to the same pointer value.
- Version tags require safe wraparound assumptions and do not by themselves make dereferences safe.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
