---
id: gc-cyclic-collection
title: "Finding unreachable counted cycles"
level: intermediate
minutes: 5
sourceLesson: gc-refcounting
summary: "Subtract candidate-internal edges from scratch counts, preserve external roots and everything they reach, then reclaim the remaining unreachable group"
---

CPython supplements strong-reference counting with a cycle collector. Its trial counts distinguish references coming from within a candidate group from references coming from the rest of the program.

## Fix 2: a cycle collector

CPython takes the belt-and-braces route: reference counting for the common case, plus a **cycle collector** in the `gc` module for the rest.

It only needs to consider **container objects** (lists, dicts, class instances), because ordinary built-in int and str instances do not contain references participating in cycles; subclasses and extension types can have different layouts. The algorithm is neat:

1. For each container being examined, copy its reference count into a scratch field.
2. For every reference *between* those containers, subtract one from the target's scratch count.
3. Anything left with a scratch count above zero is referenced from **outside** the group, so it is alive. Everything reachable from it is alive too.
4. Whatever remains is referenced only from inside the group: unreachable cycles. Free it.

Steps 1 and 2 compute, for each container, how many of its references come from outside the group:

```formula
g_X = rc_X − i_X
where
g_X: the scratch count for container X (CPython's source calls this field gc_refs)
rc_X: X's ordinary reference count
i_X: the number of references to X that come from other containers in the group being examined
In words: take an object's count and subtract the references the group itself holds; what is left are references from outside, such as local variables.
```

In the two-node example below, after `del x, y` each node has a reference count of 1 and one reference from inside the group (the other node points at it), so its scratch count is 1 − 1 = 0: nothing outside holds them, and they are freed. An object with a scratch count above zero is alive, and step 3 keeps everything reachable from it alive too, even objects whose own scratch count is 0.

```python
import gc
gc.disable()  # explicit collect still works

class Node:
    def __init__(self, name):
        self.name, self.other = name, None
    def __del__(self):
        print("freed", self.name)

x, y = Node("x"), Node("y")
# Internal strong edges keep counts nonzero.
x.other, y.other = y, x
del x, y
print("after del")
# Explicitly find the unreachable cycle.
gc.collect()
print("collected")
gc.enable()
```

Output (the two "freed" lines may come in either order):

```
after del
freed x
freed y
collected
```

After `del x, y`, each node still has a count of 1 from the other, so nothing is freed. `gc.collect()` subtracts the internal references, finds both at zero, and frees them. Since Python 3.4 (PEP 442), a Python-level __del__ no longer by itself prevents collection of an unreachable cycle. Finalizers can still resurrect objects, and some extension types have different finalization constraints; gc.garbage is not universally empty.

The collector is a **generational collector**: new containers are examined often, survivors less often, to exploit workload-dependent short object lifetimes. Scheduling depends on version/build: net allocation counts matter, and free-threaded CPython also considers process-memory growth. The thresholds are tunable with `gc.set_threshold()`.

> [!warning] Disabling the cycle collector
> gc.disable() disables automatic cyclic collection. Reference counting still operates and explicit gc.collect() still works; unreachable intact strong cycles can accumulate until explicitly collected or broken. Some services do this deliberately for predictable latency and then must avoid creating cycles.

## Where reference counting sits

| | Ref counting | Tracing GC |
|---|---|---|
| When freed | last strong release in the basic acyclic model | during collection |
| Cycles | need extra help | traced normally |
| Cost paid on | strong-reference updates and cascading release | collection and barriers |
| Destruction | prompt in basic model | runtime-specific timing |

Many systems blend the two. CPython is reference counting plus a tracing cycle collector. Research collectors use **deferred reference counting**, which skips count updates for stack variables and corrects the counts periodically, to get most of the promptness with much less overhead.

## Key takeaways
- Subtract candidate-internal edges from scratch counts, preserve external roots and everything they reach, then reclaim the remaining unreachable group.
- gc.disable stops automatic cyclic collection, while reference counting and explicit gc.collect continue to operate.
- CPython collection schedules depend on version and build; finalization and resurrection complicate the simple trial-count model.

## Further reading
- [Reference counting — Wikipedia](https://en.wikipedia.org/wiki/Reference_counting)
- [Python gc module documentation](https://docs.python.org/3/library/gc.html)
- [Python weakref module documentation](https://docs.python.org/3/library/weakref.html)
- [Automatic Reference Counting — The Swift Programming Language](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/automaticreferencecounting/)
- [Rc and reference cycles — The Rust Book](https://doc.rust-lang.org/book/ch15-06-reference-cycles.html)
- [PEP 683: Immortal objects](https://peps.python.org/pep-0683/)
- [Primary verification source 2](https://docs.python.org/3/c-api/refcounting.html)
- [Primary verification source 3](https://peps.python.org/pep-0703/)
- [Primary verification source 4](https://raw.githubusercontent.com/swiftlang/swift-book/main/TSPL.docc/LanguageGuide/AutomaticReferenceCounting.md)
- [Primary verification source 5](https://doc.rust-lang.org/std/sync/struct.Arc.html)
