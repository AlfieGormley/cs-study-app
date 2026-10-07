---
id: gc-stack-heap
title: Stack vs heap
level: basic
minutes: 10
summary: Where values live in C, Python, Java, Go and Rust, why the stack is fast but short-lived, and how escape analysis decides what goes on the heap.
---

Every value a program creates has to live somewhere in memory, and sooner or later that memory must be given back. Two common storage mechanisms are the **stack** and the **heap**. Registers, static storage and optimizations also matter; this is an introductory model, not an exhaustive classification.

The difference is about **lifetime**. A conventional call frame is reclaimed on return, while block-scoped object lifetimes can end earlier. Heap allocations can outlive the allocating call; reclamation follows ownership, reachability or explicit deallocation rather than actual future need. The rest of this module is really about the heap, so it pays to understand why the stack is the easy case.

> [!note] Scope of this module
> The Operating Systems subject covers virtual memory, pages and how `malloc` carves up memory internally. Here we take the language-level view: who decides when a value dies, and how.

## The call stack

When a function is called, the program pushes a **stack frame** holding its parameters, local variables and the return address. When the function returns, the frame is popped and all of it disappears at once.

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

Allocating a frame is just moving the **stack pointer** register by a fixed amount, usually a single instruction. Freeing it is moving the pointer back. The simple LIFO fast path needs no free-list search. Prologues, alignment, stack checks, page faults and runtime stack growth can add work; cache residency is not guaranteed.

The catch is that the stack is strictly **last in, first out**. A frame cannot outlive the call that created it, and the compiler usually needs to know each frame's size in advance.

## The heap

The **heap** is a large pool of memory where blocks can be allocated and freed in any order. Heap storage is commonly useful when:

1. A value must **outlive the function** that created it (returning a new object, storing it in a global or a long-lived data structure).
2. The **size is only known at run time** (reading a file of unknown length, a list that grows).
3. The value is **large** (a 50 MB image would blow the stack).
4. The value is **shared** between threads or parts of the program with unrelated lifetimes.

Heap allocation often costs more, although bump-pointer heap allocators also have cheap fast paths: the allocator must find a free block, record its size and later reclaim it. The really hard question is **when to free it**, because its lifetime need not coincide with the allocating call. That question is the subject of every other lesson in this module.

## The classic bug: returning a stack address

C distinguishes storage durations; it does not require a physical stack. Automatic locals commonly use frames or registers, static locals use static storage, and malloc obtains allocated storage.

```c
#include <stdlib.h>

int *bad(void) {
    int x = 42;
    return &x;   /* frame dies here */
}

int *good(void) {
    int *p = malloc(sizeof *p);
    if (!p) return NULL;
    *p = 42;
    return p;    /* caller must free */
}
```

`bad` returns the address of a slot in a frame that has already been popped. Accessing the expired object is undefined behavior regardless of whether later calls reuse that storage; no particular output or crash is guaranteed. Clang warns: *address of stack memory associated with local variable 'x' returned*. `good` returns NULL on allocation failure; on success the caller has a new duty: call `free(p)` exactly once.

## How each language places values

| Language | Stack | Heap |
|---|---|---|
| C | many automatic locals; placement optimized | allocated storage from malloc |
| CPython | implementation-specific interpreter frames | most objects; some shared/static objects |
| Java | local slots conceptually; may be registers | objects in JVM model; allocations may be eliminated |
| Go | non-escaping values | escaping values |
| Rust | local values often inline or registers | owned allocations through Box, Vec, String |

### Python: names reference managed objects

CPython represents values as objects with type and reference-management metadata. Most are dynamically allocated; some singleton/static objects and immortal objects are exceptions, and free-threaded builds have different counting details. A few, such as small integers and `None`, are created once when the interpreter starts and shared. A local variable is just a name in the frame that **refers** to an object.

```python
def make():
    xs = [1, 2, 3]   # list object on heap
    return xs        # return the reference

a = make()       # list survives the call
```

The list survives this call because `a` still refers to it. That is why "stack vs heap" rarely comes up in Python: you never place anything yourself, and the runtime manages reclamation; cycles and finalization complicate promptness (lesson 3).

### Java: primitives and references on the stack, objects on the heap

In Java, a local `int` lives in the frame, and so does a local reference variable, but the object it points to is always (semantically) on the heap.

```java
void f() {
    int n = 10;            // in frame
    int[] a = new int[n];  // ref in frame,
                           // array on heap
}
```

The HotSpot JIT compiler performs **escape analysis**: if it can prove an object never leaves the method, it may eliminate the allocation entirely and keep the fields in registers ("scalar replacement"). You cannot request this; it is an optimisation.

### Go: the compiler decides with escape analysis

Go makes escape analysis visible. You can return a pointer to a local variable, and it is perfectly safe:

```go
type Point struct{ X, Y int }

func newPoint() *Point {
    p := Point{1, 2}
    return &p   // fine in Go
}
```

Analyzed as a non-inlined function returning an escaping pointer, p requires storage surviving the call and the standard compiler normally heap-allocates it. Inlining can change the result at a particular call site. Use go build -gcflags=-m to inspect decisions; nonescaping values can still need heap storage for implementation reasons such as size.

Things that commonly force a value to escape in Go: returning its address, storing it in a global or a heap object, capturing it in a closure that outlives the call, or storing an interface value in an escaping location. Merely forming a pointer or interface does not universally force heap allocation.

### Rust: ownership and explicit allocations

Rust values can live in locals, registers, static storage or inside another allocation. Box owns a heap allocation, while Vec and String usually own buffers. A local Vec or String commonly has inline pointer/length/capacity metadata; a Box<T> for sized T has a pointer-sized representation, not those three fields, and the buffer is freed automatically when the owner goes out of scope (lesson 6).

```
 let v = vec![1, 2, 3];

 stack            heap
 +----------+     +---+---+---+
 | ptr  ----+---> | 1 | 2 | 3 |
 | len  = 3 |     +---+---+---+
 | cap  = 3 |
 +----------+
```

## Stack limits and stack overflow

Stacks are small compared with the heap, and each thread has its own.

| Runtime | Typical stack size |
|---|---|
| Linux main thread | configured limit; inspect ulimit -s |
| JVM platform thread | platform/version-dependent; configure -Xss |
| Go standard runtime goroutine | small growable stack; implementation-dependent |
| CPython | interpreter recursion limit; inspect sys.getrecursionlimit() |

Deep or unbounded recursion overflows the stack: a segmentation fault in C, `StackOverflowError` in Java, a fatal "goroutine stack exceeds" error in Go (the default maximum is 1 GB on 64-bit), and `RecursionError` in Python (which counts frames rather than bytes).

Goroutine stacks are a neat trick. They start tiny and, when a function needs more room, the runtime allocates a bigger stack and copies the old one across, fixing up pointers into it. That is why a Go program can run hundreds of thousands of goroutines when the same number of 1 MB OS-thread stacks would not fit.

> [!warning] Big arrays on the stack
> If double is 8 bytes and the array is materialized on the stack, `double grid[2000][2000];` needs 32,000,000 bytes, exceeding an 8 MiB stack budget. Allocate it on the heap instead.

> [!note] Limits of this model
> A universal stack size or allocation latency is omitted: neither is guaranteed across runtimes, operating systems and compiler settings. Dynamic size and sharing alone do not require heap storage (C VLAs and safely scoped sharing are counterexamples).

## Value and reference semantics

Placement is tied to what assignment means:

- **Value semantics**: assignment copies the data. C structs, Go structs and arrays, and Rust's `Copy` types behave this way.
- **Reference semantics**: assignment copies a pointer, so two names share one object. Python objects and Java objects behave this way.

```python
a = [1, 2]
b = a          # same list, not a copy
b.append(3)
print(a)       # [1, 2, 3]
```

Shared heap objects are exactly what makes deallocation hard: you can only free the list when **neither** `a` nor `b` can reach it.

## Trade-offs at a glance

| | Stack | Heap |
|---|---|---|
| Allocate | move a pointer | allocator call |
| Free | automatic, at return | manual or GC |
| Lifetime | the call | any |
| Size | fixed, small | flexible, large |

Performance-minded code in managed languages tries to **avoid heap allocation in hot loops**: reuse buffers, prefer values over pointers in Go, and let escape analysis keep short-lived objects off the heap. Every avoided allocation is also work the garbage collector never has to do.

## Key takeaways
- Conventional call frames use LIFO allocation; physical placement and object lifetimes depend on the language and implementation.
- The heap holds anything that outlives its creator, is sized at run time, is large or is shared; deciding when to free it is the hard problem.
- C exposes storage duration and allocated storage; managed runtimes choose representations and may eliminate allocations; Rust separates ownership from physical storage placement.
- Returning a pointer to a local is a bug in C but safe in Go, because Go's compiler moves the value to the heap.
- Stacks are small (megabytes per thread, kilobytes per goroutine), so deep recursion and large local arrays overflow them.

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
