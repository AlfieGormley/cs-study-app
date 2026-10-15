---
id: gc-storage-lifetimes
title: "Storage and object lifetimes"
level: basic
minutes: 5
sourceLesson: gc-stack-heap
summary: "A conventional call stack reclaims frames in last-in, first-out order; language storage durations and optimisations are more general"
---

Programs need storage for materialised values, and finite storage eventually needs to be reused. Optimisation can remove a value entirely; long-lived storage can remain until process exit. Two common storage mechanisms are the **call stack** and **heap memory**, usually just called "the stack" and "the heap". Registers, static storage and optimizations also matter; this is an introductory model, not a complete classification.

The difference is about **object lifetime**: how long a value stays valid. A conventional call frame is reclaimed on return, while block-scoped object lifetimes can end earlier. Heap allocations can outlive the allocating call; reclamation follows ownership, reachability or explicit deallocation rather than actual future need. The rest of this module is really about the heap, so it pays to understand why the stack is the easy case.

> [!note] Scope of this module
> The Operating Systems subject covers virtual memory, pages and how `malloc` carves up memory internally. Here we take the language-level view: who decides when a value dies, and how.

## The call stack

In a conventional stack implementation, an active call has a **stack frame** for saved state and locals that need memory. Parameters and the return address may instead be held in registers, and optimisation can remove frames. Returning reclaims that frame; individual language-level object lifetimes can end earlier.

```
 main() calls area(), which calls sq()

 high addresses
 +----------------------+
 | main:  w=3, h=4      |
 +----------------------+
 | area:  a=3, b=4      |
 |        ret -> main   |
 +----------------------+
 | sq:    n=3           |  <- stack pointer
 |        ret -> area   |
 +----------------------+
 low addresses (grows down on x86/ARM)
```

A conventional fixed-size frame can have a fast path that moves the **stack pointer** register by a fixed amount, sometimes in one instruction. Freeing it is moving the pointer back. The simple LIFO fast path needs no free-list search. Function prologues, stack alignment, stack checks, page faults and runtime stack growth can add work; cache residency is not guaranteed.

The catch is that the stack is strictly **last in, first out**. A conventional frame belongs to its active call. Many frames have a statically known size, though C variable-length arrays and other dynamic stack allocations are counterexamples.

## The heap

The **heap** is a large pool of memory where blocks can be allocated and freed in any order. Heap storage is commonly useful when:

1. A value must **outlive the function** that created it (returning a new object, storing it in a global or a long-lived data structure).
2. The **size is only known at run time** (reading a file of unknown length, a list that grows).
3. The value is **large** (a 50 MB image would blow the stack).
4. The value is **shared** between threads or parts of the program with unrelated lifetimes.

Heap allocation often costs more, although bump-pointer heap allocators also have cheap fast paths: the allocator must find a free block, record its size and later reclaim it. The really hard question is **when to free it**, because its lifetime need not coincide with the allocating call. That question is the subject of every other lesson in this module.

## Trade-offs at a glance

| | Stack | Heap |
|---|---|---|
| Allocate | move a pointer | allocator call |
| Free | automatic, at return | manual or GC |
| Lifetime | active frame | allocation contract |
| Size | bounded; often fixed | allocator limits |

Performance-minded code in managed languages tries to **avoid heap allocation in hot loops**: reuse allocations, prefer values over pointers in Go, and let escape analysis keep short-lived objects off the heap. Every avoided allocation is also work the garbage collector never has to do.

## Key takeaways
- A conventional call stack reclaims frames in last-in, first-out order; language storage durations and optimisations are more general.
- Heap storage permits lifetimes independent of a call, but dynamic size, sharing and large size alone do not logically require it.
- Allocation fast paths are implementation choices; stack checks, allocator bookkeeping and reclamation add work.

## Further reading
- [Stack-based memory allocation — Wikipedia](https://en.wikipedia.org/wiki/Stack-based_memory_allocation)
- [Escape analysis — Wikipedia](https://en.wikipedia.org/wiki/Escape_analysis)
- [A Guide to the Go Garbage Collector (escape analysis section) — go.dev](https://go.dev/doc/gc-guide)
- [Go FAQ: stack or heap? — go.dev](https://go.dev/doc/faq#stack_or_heap)
- [What is ownership? (stack and heap) — The Rust Book](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 2](https://doc.rust-lang.org/std/vec/struct.Vec.html)
- [Primary verification source 3](https://go.dev/src/runtime/stack.go)
- [Primary verification source 4](https://docs.python.org/3/c-api/refcounting.html)
