---
id: gc-roots-mark-compact
title: "Roots, marking and compaction"
level: intermediate
minutes: 5
sourceLesson: gc-tracing
summary: "Tracing follows strong paths from roots, so an unreachable cycle needs no special case"
---

Reference counting asks each object "does anything point at you?". A **tracing garbage collector** asks a better question: "can the program still **reach** you?".

It starts from the places the program can see directly, follows every pointer, and treats everything it did not reach as garbage. Cycles are not a special case: an unreachable cycle is simply never visited. Java, C#, Go, JavaScript, Haskell, OCaml and Ruby all use tracing collectors.

## Roots and reachability

The **GC roots** are the references the running program can use without following any other pointer:

- local variables and temporaries in every thread's **stack frames** and CPU **registers**
- **global** and static variables
- runtime internals (for example JNI handles in the JVM, or the interpreter's own tables)

A **live object** is one with a path to it from a root. Everything else is garbage, even if other garbage points at it.

```
 roots: [a] [b]
         |   |
         v   v
         A   C        D <--> E
         |                (cycle, no root)
         v
         B
 live: A, B, C      garbage: D, E
```

Note that "reachable" is an over-approximation of "will be used". A reachable object you will never touch again is a leak the collector cannot see.

## Mark-sweep

McCarthy's 1960 Lisp paper describes the classic mark-and-reclaim approach. The basic mark-sweep model has two phases.

1. **Mark.** Walk the object graph from the roots, setting a mark bit in each object reached.
2. **Sweep.** Walk the whole heap. Unmarked objects go back on a free list; marked ones have their bit cleared ready for next time.

The mark phase is just graph traversal. Here it is on a toy heap:

```python
heap = {
    "A": ["B"], "B": [], "C": [],
    "D": ["E"], "E": ["D"],
}
roots = ["A", "C"]

def mark(roots):
    marked, stack = set(), list(roots)
    while stack:
        obj = stack.pop()
        # Visit cycles only once per object.
        if obj not in marked:
            marked.add(obj)
            # Add its outgoing references.
            stack.extend(heap[obj])
    return marked

live = mark(roots)
# Unvisited identifiers form toy garbage.
dead = [o for o in heap if o not in live]
print(sorted(live), dead)
```

Output:

```
['A', 'B', 'C'] ['D', 'E']
```

Collectors commonly use explicit worklists, bounded recursion or other traversal strategies so a long chain does not exhaust the native call stack. This toy algorithm assumes every referenced identifier names a heap object.

**Costs.** In a simple model with bounded pointer fields per object, marking grows with roots and **live** data; sweeping examines the **whole heap** or its allocation metadata. Pointer density and implementation details affect actual work. Mark-sweep never moves objects, which makes it simple and friendly to C code holding raw pointers. The downside is **heap fragmentation**: after many cycles, free space is scattered in small holes, so allocation must search free lists and a large request can fail even though plenty of total memory is free.

## Mark-compact

**Mark-compact** fixes fragmentation by sliding live objects together after marking, so all free space is one contiguous block at the end.

```
 before: [A][ ][B][ ][ ][C][ ]
 after:  [A][B][C][          ]
                  ^ allocate here
```

Allocation becomes a **bump pointer**: hand out the next block of the requested size and advance the pointer, just like the stack:

```formula
a = p
p' = p + N
where
a: the address handed to the program for the new object
p: the bump pointer before the request: the address of the first free byte
p': the bump pointer afterwards
N: the size of the requested object, in bytes, rounded up for alignment
In words: the new object starts where free space starts, and the pointer moves past it; the allocator also checks that p' has not run past the end of the free area.
```

For example, with the pointer at address 1,000 a 48-byte request returns address 1,000 and leaves the pointer at 1,048. The price is extra passes over the heap: compute each object's new address, rewrite every pointer to it, then move it. HotSpot's Serial and Parallel collectors compact the old generation this way.

## Key takeaways
- Tracing follows strong paths from roots, so an unreachable cycle needs no special case.
- Plain mark-sweep reclaims unmarked objects without relocating survivors and can leave fragmented free space.
- Compaction packs movable live objects and updates references, enabling a bump-allocation fast path with capacity and alignment checks.

## Further reading
- [Tracing garbage collection — Wikipedia](https://en.wikipedia.org/wiki/Tracing_garbage_collection)
- [Cheney's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Cheney%27s_algorithm)
- [HotSpot VM garbage collection tuning guide: generations — Oracle](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-collector-implementation.html)
- [The Garbage Collection Handbook (Jones, Hosking, Moss)](https://gchandbook.org/)
- [Boehm-Demers-Weiser conservative garbage collector](https://www.hboehm.info/gc/)
- [McCarthy: Recursive Functions of Symbolic Expressions (1960)](https://www-formal.stanford.edu/jmc/recursive.pdf)
- [Primary verification source 2](https://go.dev/doc/gc-guide)
- [Primary verification source 3](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-garbage-collector-tuning.html)
