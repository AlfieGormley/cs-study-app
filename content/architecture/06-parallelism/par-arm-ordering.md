---
id: par-arm-ordering
title: Arm ordering, message passing and multicopy atomicity
level: intermediate
minutes: 3
sourceLesson: par-memory-models
summary: Arm barriers, dependencies and ordered instructions provide different contracts.
---

## ARM: weakly ordered

For ordinary Normal-memory accesses to independent addresses, the AArch64 model permits all four broad reorderings unless a dependency, barrier or ordered instruction constrains them. These labels summarise observable behaviour rather than a physical implementation. The hardware is free to let a later load overtake an earlier one, or to drain stores to memory out of order.

What forces order on ARM:

- **Data dependencies.** An actual machine-level address dependency can order the dependent access. A C/C++ source expression such as `p = head; v = p->val` does not by itself establish a safe inter-thread publication protocol; use appropriate atomics and lifetime rules.
- **Barriers.** For the relevant observers in the inner-shareable domain, `DMB ISH` orders the required earlier and later data accesses; it is not an instruction barrier or a general cache flush. `DMB ISHST` orders stores with stores; `DMB ISHLD` orders loads with later loads and stores.
- **Acquire and release instructions.** `LDAR` (load-acquire) prevents later accesses moving before it. `STLR` (store-release) prevents earlier accesses moving after it. FEAT_LRCPC provides `LDAPR`, an RCpc acquire with weaker ordering in some patterns than `LDAR`; instruction availability and performance depend on the target.

The classic victim is the **message-passing litmus test** (MP):

```
data = flag = 0
Thread 1         Thread 2
data = 42        r1 = flag
flag = 1         r2 = data
```

Can Thread 2 end with `r1 == 1` and `r2 == 0`, that is, the flag set but the data stale? On x86, no: stores leave in order, and loads are not reordered with loads. On ARM, yes: either the two stores or the two loads may be reordered. These are machine-level litmus tests. Using unsynchronised ordinary shared C/C++ objects would already be a data race and undefined behaviour on either target.

### Multi-copy atomicity

A subtler property is **other-multi-copy atomicity**: after a write becomes observable to another observer, the model requires a consistent propagation order to the remaining observers, while the issuing thread may read its own buffered write early. This is not a zero-latency physical event. The revised Armv8-A model described by Pulte et al. and x86-TSO have this property.

For the **IRIW** test, two writers independently update x and y, while two readers read them in opposite orders. If each reader’s loads are suitably ordered at the hardware level, a multicopy-atomic model forbids the readers from observing opposite write orders. A non-multicopy-atomic model can allow it. Language-level acquire operations and different hardware barriers are not interchangeable; specify the actual mapping when comparing architectures.

## Key takeaways
- Arm barriers, dependencies and ordered instructions provide different contracts.
- Hardware litmus tests must specify memory type, access ordering and observer scope.

## Further reading
- [Lamport’s original sequential-consistency paper](https://lamport.azurewebsites.net/pubs/multi.pdf)
- [The x86-TSO model](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)
- [The revised Arm multicopy-atomic model](https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf)
- [C++ draft: races](https://eel.is/c++draft/intro.races)
- [C++ draft: atomic ordering](https://eel.is/c++draft/atomics.order)
