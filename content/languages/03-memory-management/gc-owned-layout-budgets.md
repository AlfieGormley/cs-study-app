---
id: gc-owned-layout-budgets
title: "Owned buffers and stack budgets"
level: basic
minutes: 5
sourceLesson: gc-stack-heap
summary: "Vec and String own heap buffers through local metadata; Box has a different representation, and zero-sized or empty allocations are special cases"
---

Ownership and physical placement answer different questions. A small local handle can own a large allocation elsewhere; a stack budget must account for the storage actually materialised in frames.

## Rust: ownership and explicit allocations

Rust values can live in locals, registers, static storage or inside another allocation. Box owns a heap allocation, while Vec and String usually own a heap buffer. A local Vec or String commonly has inline pointer/length/capacity metadata; a Box<T> for sized T has a pointer-sized representation, not those three fields, and its heap buffer is freed automatically when the owner goes out of scope.

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

Conventional OS threads have their own stacks; the standard Go runtime also manages separate goroutine stacks. Stack limits and growth policies differ from the available heap.

| Runtime | Typical stack size |
|---|---|
| Linux main thread | configured limit; inspect ulimit -s |
| JVM platform thread | platform/version-dependent; configure -Xss |
| Go standard runtime goroutine | small growable stack; implementation-dependent |
| CPython | interpreter recursion limit; inspect sys.getrecursionlimit() |

Deep recursion can exhaust a stack or encounter a runtime recursion guard. A C program has no language-guaranteed stack-overflow exception; a protected stack commonly faults. Java may throw `StackOverflowError`. The standard Go runtime reports a fatal stack-limit error; debug.SetMaxStack documents an initial maximum of 1,000,000,000 bytes on 64-bit systems. Python raises `RecursionError` at its interpreter recursion limit; excessive limits can still crash a process.

Goroutine stacks are a neat trick. They start tiny and, when a function needs more room, the runtime allocates a bigger stack and copies the old one across, fixing up pointers into it. That is why a Go program can run hundreds of thousands of goroutines when the same number of 1 MB OS-thread stacks would not fit.

> [!warning] Big arrays on the stack
> If double is 8 bytes and the array is materialized on the stack, `double grid[2000][2000];` needs 32,000,000 bytes, exceeding an 8 MiB stack budget. Allocate it on the heap instead.

To check whether a local array fits, multiply its element count by the size of one element and compare the result with the thread's stack budget:

```formula
S_grid = 2000 × 2000 × 8 B
S_grid = 32,000,000 B
S_stack = 8 MiB = 8 × 1,048,576 B
S_stack = 8,388,608 B
S_grid / S_stack ≈ 3.8
where
S_grid: the memory the array needs, in bytes (B): rows × columns × bytes per element
2000: the number of rows, and also the number of columns, in grid[2000][2000]
8: the size of one C double (a 64-bit floating-point number) on common platforms, in bytes
S_stack: the thread's stack budget, in bytes; 8 MiB is a common Linux default for the main thread, but it is configurable
B: bytes; one byte is 8 bits
MiB: mebibyte, 2^20 = 1,048,576 bytes (binary prefix; a megabyte, MB, is 1,000,000 bytes)
≈: approximately equal to (the result is rounded)
In words: the array needs about 3.8 times the whole stack budget, before counting any other frame, so it cannot fit.
```

The same multiplication works for any fixed-size local: a 100-row, 100-column grid of eight-byte doubles needs 80,000 bytes and fits within the illustrative 8 MiB budget when that much space remains. The budget is not fixed: it depends on the operating system, `ulimit -s` and how the thread was created.

> [!note] Limits of this model
> A universal stack size or allocation latency is omitted: neither is guaranteed across runtimes, operating systems and compiler settings. Dynamic size and sharing alone do not require heap storage (C VLAs and safely scoped sharing are counterexamples).

## Key takeaways
- Vec and String own heap buffers through local metadata; Box has a different representation, and zero-sized or empty allocations are special cases.
- Thread and goroutine stack budgets depend on runtime, platform and configuration; recursion limits are not interchangeable with byte limits.
- Compare a materialised array's byte requirement with the whole available stack budget, including existing frames and other overhead.

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
