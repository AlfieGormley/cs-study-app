---
id: dist-crdt-observed-remove
title: Observed-remove sets and tombstone safety
level: advanced
minutes: 3
summary: Trace tagged adds and removes, then identify what an offline replica means for metadata collection.
sourceLesson: dist-crdts-gossip
---

Counters can preserve an update history by growing vectors. Sets need a way to record removals without letting an old replica’s add silently undo them.

### G-Set and 2P-Set

A **G-Set** only grows; merge is union. A **2P-Set** adds a "tombstone" set of removed elements; an element is present if it's in the add-set and not the remove-set. Its flaw: once removed, an element can **never be re-added**.

### OR-Set (observed-remove set)

The OR-Set fixes that. Every `add(x)` attaches a **unique tag** (e.g. replica id + counter). `remove(x)` removes only the tags the remover has **observed**.

```
A: add(milk) tag a1
   -> sync to B
B: remove(milk)  removes {a1}
A: add(milk) tag a2   (concurrent)
merge:
 adds   = {a1, a2}
 removes= {a1}
 milk present (tag a2 survives)
```

Concurrent add and remove resolves to **add wins**, which is usually what users expect (re-adding milk to the shopping list shouldn't be cancelled by someone else's earlier removal). Riak's sets and maps, Redis CRDB sets and Automerge's internals use this idea.

### Beyond sets

- **LWW-Register / MV-Register**: a single value, resolved by timestamp or kept as multiple values.
- **Maps** of CRDTs, recursively.
- **Sequence CRDTs** (RGA, Logoot, Yjs, Automerge) for collaborative text editing, as in many live collaborative editors.

Costs: metadata grows (tags and tombstones accumulate and need garbage collection). Arbitrary independent updates cannot preserve every invariant; bounded counters can enforce non-negative stock using preallocated rights, as described above.

Garbage-collecting tombstones is the hard part. A tombstone can only be dropped once **every** replica has seen it; otherwise a replica that was offline still holds the old add, and the next merge brings the element back. Knowing that every replica has caught up is itself a coordination problem, the same one behind Cassandra's `gc_grace_seconds` in the earlier background-repair unit. (Optimised OR-Sets such as Riak's ORSWOT avoid most tombstones by using version vectors, but pay in vector size instead.)

> [!tip] Choosing
> Use a CRDT when its merge semantics and permitted updates preserve your application's requirements. Invariants incompatible with independent updates need coordination or a design such as preallocated escrow rights.

## Key takeaways
- Grow-only sets merge by union; a two-phase set cannot re-add an element after removal.
- An OR-Set removes only observed add tags, so an unobserved concurrent add survives.
- Discarding removal metadata before every relevant replica has caught up can resurrect data; richer CRDTs also pay metadata costs.

## Further reading
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [A comprehensive study of CRDTs (Shapiro et al.)](https://www.lip6.fr/Marc.Shapiro/papers/2011/Comprehensive-CRDTs-RR7506-2011-01.pdf)
- [crdt.tech: resources and implementations](https://crdt.tech/)
- [CRDTs: the hard parts (Martin Kleppmann)](https://martin.kleppmann.com/2020/07/06/crdt-hard-parts-hydra.html)
