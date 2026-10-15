---
id: gc-copying-precision
title: "Copying collection and pointer precision"
level: intermediate
minutes: 3
sourceLesson: gc-tracing
summary: "Cheney's scan and free pointers implement a breadth-first work queue within to-space, with forwarding records avoiding duplicate copies"
---

A collector can reclaim a region by copying its reachable survivors elsewhere. The semispace model makes the trade-off clear: compact allocation and survivor-only copying in exchange for spare space and relocation work.

## Copying collection

The simple **semispace copying collector** splits its managed region into two equal spaces. Other copying collectors use different region layouts. The program allocates in **from-space** with a bump pointer. When it fills:

1. Copy each object reachable from the roots into **to-space**, packed tightly.
2. Leave a **forwarding pointer** in the old copy, so later references to it can be redirected to the new address.
3. Swap the roles of the two halves. Everything left in the old half is garbage and is discarded **without being looked at**.

The usual object-graph presentation of Cheney's 1970 algorithm does this breadth-first with a scan pointer and a free pointer into to-space, without a separate traversal stack. The original paper describes list structures; this diagram uses general objects:

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

**Why it is attractive.** Apart from root scanning and fixed costs, copying and scanning work grows with **live data and its reference fields**. If 2% of the half-space is live, the collector touches that 2% and frees the other 98% for nothing. There is no fragmentation and allocation is a pointer bump.

**Why it is not used for everything.** The simple semispace model reserves two equal spaces while using one for allocation; this is not a promise that total process memory doubles. Repeatedly copying large, long-lived objects adds work. It also **moves** objects, so references to moved objects must be found and updated safely, or handled through a suitable indirection or pinning protocol.

> [!note] Precise vs conservative
> A **precise collector** knows the exact location of every pointer, from type information and compiler-generated stack maps. A **conservative collector**, such as the Boehm GC used with C and C++, treats any word that looks like a heap address as a possible pointer. It cannot safely relocate objects retained by ambiguous words by rewriting those words (they might be integers); hybrid mostly-copying designs can still move other objects, and it may keep garbage alive by mistake, but it works without compiler help.

## Comparing the three

| | Cost grows with | Moves? | Fragments? |
|---|---|---|---|
| Mark-sweep | live + heap | no | yes |
| Mark-compact | live + heap | yes | no |
| Copying | live | yes | no |

## Key takeaways
- Cheney's scan and free pointers implement a breadth-first work queue within to-space, with forwarding records avoiding duplicate copies.
- A simple semispace collector reserves two spaces while allocating into one; its total work also includes roots and pointer fields.
- Ambiguous machine words cannot safely be rewritten as pointers; mostly-copying designs pin ambiguously referenced objects while moving others.

## Further reading
- [Tracing garbage collection — Wikipedia](https://en.wikipedia.org/wiki/Tracing_garbage_collection)
- [Cheney: A Nonrecursive List Compacting Algorithm (1970)](https://people.cs.umass.edu/~emery/classes/cmpsci691s-fall2004/papers/p677-cheney.pdf)
- [HotSpot VM garbage collection tuning guide: generations — Oracle](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-collector-implementation.html)
- [The Garbage Collection Handbook (Jones, Hosking, Moss)](https://gchandbook.org/)
- [Boehm-Demers-Weiser conservative garbage collector](https://www.hboehm.info/gc/)
- [Primary verification source 2](https://go.dev/doc/gc-guide)
- [Primary verification source 3](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-garbage-collector-tuning.html)
