---
id: gc-tracing
title: Tracing GC: mark-sweep, copying and generational
level: intermediate
minutes: 14
summary: How tracing collectors find live objects from the roots, the three classic designs (mark-sweep, mark-compact and copying), why most objects die young, and how generational collectors with write barriers exploit that.
---

Reference counting asks each object "does anything point at you?". A **tracing** garbage collector asks a better question: "can the program still **reach** you?".

It starts from the places the program can see directly, follows every pointer, and treats everything it did not reach as garbage. Cycles are not a special case: an unreachable cycle is simply never visited. Java, C#, Go, JavaScript, Haskell, OCaml and Ruby all use tracing collectors.

## Roots and reachability

The **roots** are the references the running program can use without following any other pointer:

- local variables and temporaries in every thread's **stack frames** and CPU **registers**
- **global** and static variables
- runtime internals (for example JNI handles in the JVM, or the interpreter's own tables)

An object is **live** if there is a path to it from a root. Everything else is garbage, even if other garbage points at it.

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

Note that "reachable" is an over-approximation of "will be used". A reachable object you will never touch again is a leak the collector cannot see (lesson 2).

## Mark-sweep

The oldest design, from John McCarthy's 1960 Lisp, has two phases.

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
        if obj not in marked:
            marked.add(obj)
            stack.extend(heap[obj])
    return marked

live = mark(roots)
dead = [o for o in heap if o not in live]
print(sorted(live), dead)
```

Output:

```
['A', 'B', 'C'] ['D', 'E']
```

Real collectors use an explicit mark stack like this rather than recursion, because a long linked list would otherwise overflow the native stack.

**Costs.** Marking is proportional to the **live** data; sweeping is proportional to the **whole heap**. Mark-sweep never moves objects, which makes it simple and friendly to C code holding raw pointers. The downside is **fragmentation**: after many cycles, free space is scattered in small holes, so allocation must search free lists and a large request can fail even though plenty of total memory is free.

## Mark-compact

**Mark-compact** fixes fragmentation by sliding live objects together after marking, so all free space is one contiguous block at the end.

```
 before: [A][ ][B][ ][ ][C][ ]
 after:  [A][B][C][          ]
                  ^ allocate here
```

Allocation becomes a **bump pointer**: hand out the next N bytes and advance the pointer, just like the stack. The price is extra passes over the heap: compute each object's new address, rewrite every pointer to it, then move it. HotSpot's Serial and Parallel collectors compact the old generation this way.

## Copying collection

A **copying** (semispace) collector splits the heap into two halves. The program allocates in **from-space** with a bump pointer. When it fills:

1. Copy each object reachable from the roots into **to-space**, packed tightly.
2. Leave a **forwarding pointer** in the old copy, so later references to it can be redirected to the new address.
3. Swap the roles of the two halves. Everything left in the old half is garbage and is discarded **without being looked at**.

Cheney's 1970 algorithm does this breadth-first with just two pointers into to-space and no stack:

```
 to-space after copying roots A, C:
 [A][C]
  ^scan  ^free

 scan A: copy its child B to free
 [A][C][B]
     ^scan  ^free

 scan C, then B: no new children
 [A][C][B]
           ^scan == free: done
```

Objects between `scan` and `free` are copied but not yet scanned; when `scan` catches `free`, the work is done.

**Why it is attractive.** The cost is proportional to **live data only**. If 2% of the half-space is live, the collector touches that 2% and frees the other 98% for nothing. There is no fragmentation and allocation is a pointer bump.

**Why it is not used for everything.** It needs twice the memory, and copying large, long-lived objects again and again is wasteful. It also **moves** objects, so the collector must know precisely which words are pointers.

> [!note] Precise vs conservative
> A **precise** collector knows the exact location of every pointer, from type information and compiler-generated stack maps. A **conservative** collector, such as the Boehm GC used with C and C++, treats any word that looks like a heap address as a possible pointer. It cannot safely relocate objects retained by ambiguous words by rewriting those words (they might be integers); hybrid mostly-copying designs can still move other objects, and it may keep garbage alive by mistake, but it works without compiler help.

## Comparing the three

| | Cost ∝ | Moves? | Fragments? |
|---|---|---|---|
| Mark-sweep | live + heap | no | yes |
| Mark-compact | live + heap | yes | no |
| Copying | live | yes | no |

## The generational hypothesis

Many workloads have the useful empirical pattern that most allocations become unreachable quickly, but survival rates and lifetimes are workload-dependent. Temporary strings, iterators, boxed numbers and request-scoped objects are common examples. A minority, such as caches and configuration, live for the whole run.

**Generational** collectors exploit this by splitting the heap by age:

```
 young generation        old generation
 +------+-----+-----+    +---------------+
 | eden | S0  | S1  | -> |  tenured      |
 +------+-----+-----+    +---------------+
  new objects here        survivors promoted
```

- New objects are bump-allocated in the **young** generation (classic HotSpot generational collectors use eden and survivor spaces; G1 uses regions).
- When it fills, a **minor collection** copies its few survivors out. Because the young generation is small and mostly dead, this is fast, with a pause depending on live bytes, root scanning and the implementation.
- Objects that survive several minor collections are **promoted** (tenured) to the **old** generation.
- The old generation is usually examined less often. Terminology varies: an old-generation or major cycle need not be a full-heap stop-the-world collection.

> [!example] Rough numbers
> In a simplified fill-and-collect model, a service allocates 500 MB/s into 250 MB of available young allocation space. Ignoring pause time and survivor-space overhead, it fills in 0.5 s. If 2% of those bytes survive, each collection copies about 5 MB. The other 245 MB is reclaimed without being touched.

## The catch: old-to-young pointers

A minor collection only traces the young generation. But an old object can point at a young one:

```java
cache.put(key, new Entry()); // old->young
```

If that `Entry` is reachable only through `cache`, a minor GC that ignored the old generation would free it while still in use. Scanning the whole old generation every time would defeat the point.

The answer is a **write barrier**: code associated with relevant reference stores, with redundant barriers sometimes eliminated. When the program writes a pointer into an old object, the barrier records it. A common HotSpot configuration divides memory into 512-byte cards; collector/version settings can change the granularity. A card-based collector records relevant reference stores in a card table. At a minor GC, only dirty cards are scanned as extra roots. Other designs keep a **remembered set** of the exact slots.

This is the real cost of generational GC: relevant pointer writes may pay a small tax (some barriers are elided or use different mechanisms), in exchange for cheap minor collections.

## Stop-the-world and safepoints

Collectors move objects and read the stacks, so the classic approach is to **stop the world**: pause every application thread, collect, then resume. In a conventional precise stop-the-world design, threads are brought to safepoints, places where the compiler has recorded exactly where every pointer is (for example, at method calls and loop back-edges).

Pause length grows with the work: a minor GC pause tracks the survivors, while a full mark-compact of a 30 GB old generation can pause for seconds. Lesson 5 covers how modern collectors do most of that work concurrently.

## The space-time trade-off

In a steady-state model with fixed live size, allocation rate and dominant marking cost, each collection costs roughly the live data and yields about the spare room. Ignoring sweep, root and fixed overhead:

```
 GC work per byte allocated
   ~ live / (heap - live)

 live 1 GB, heap 1.5 GB -> ~2
 live 1 GB, heap 3 GB   -> ~0.5
```

Here the total heap doubles, but headroom grows from 0.5 GB to 2 GB: fourfold, so this model predicts four times less work per allocated byte. That is why GC languages often run with heaps two or more times their live data, and why Go exposes the trade-off directly as `GOGC` (lesson 5). Tracing GC buys safety and throughput with memory.

## Key takeaways
- A tracing collector frees everything not reachable from the roots (stacks, registers, globals); cycles need no special handling.
- Mark-sweep doesn't move objects but fragments the heap; mark-compact removes fragmentation with extra passes; copying collection costs only live data but needs twice the space.
- Most objects die young, so generational collectors copy a small young generation often and collect the old generation rarely.
- Old-to-young pointers are tracked with write barriers and card tables, which put a small cost on every pointer store.
- Collection work falls sharply as heap headroom grows: GC trades memory for CPU time.

## Further reading
- [Tracing garbage collection — Wikipedia](https://en.wikipedia.org/wiki/Tracing_garbage_collection)
- [Cheney's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Cheney%27s_algorithm)
- [HotSpot VM garbage collection tuning guide: generations — Oracle](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-collector-implementation.html)
- [The Garbage Collection Handbook (Jones, Hosking, Moss)](https://gchandbook.org/)
- [Boehm-Demers-Weiser conservative garbage collector](https://www.hboehm.info/gc/)
- [Primary verification source 2](https://go.dev/doc/gc-guide)
- [Primary verification source 3](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-garbage-collector-tuning.html)
