---
id: gc-escape-placement
title: "Placement and escape analysis"
level: basic
minutes: 3
sourceLesson: gc-stack-heap
summary: "HotSpot escape analysis can eliminate an object allocation through scalar replacement; it does not promise to put every non-escaping object on a stack"
---

The language model describes observable behaviour; a compiler may use registers, inline fields or eliminate allocations while preserving it. This table is a starting model, not a physical-layout guarantee.

## How each language places values

| Language | Stack | Heap |
|---|---|---|
| C | many automatic locals; placement optimized | allocated storage from malloc |
| CPython | interpreter frames (details vary by version) | most objects; some shared or static objects |
| Java | local slots conceptually; may be registers | objects in JVM model; allocations may be eliminated |
| Go | non-escaping values | escaping values |
| Rust | local values often inline or registers | owned allocations through Box, Vec, String |



## Java: frame values and semantic heap objects

The JVM model gives methods local-variable slots and places class instances and arrays in the heap. Machine-code placement can differ: HotSpot can keep locals in registers or eliminate an allocation while preserving observable behaviour.

```java
void f() {
    int n = 10;            // in frame
    // JVM model: a refers to a new array.
    int[] a = new int[n];  // ref in frame,
                           // array on heap
}
```

The HotSpot JIT compiler performs **escape analysis**: if it can prove an object never leaves the method, it may eliminate the allocation entirely and keep the fields in registers ("scalar replacement"). You cannot request this; it is an optimisation.

## Go: the compiler decides with escape analysis

Go makes escape analysis visible. You can return a pointer to a local variable, and it is perfectly safe:

```go
type Point struct{ X, Y int }

func newPoint() *Point {
    p := Point{1, 2}
    // The pointed-to value must survive.
    return &p   // fine in Go
}
```

Analyzed as a non-inlined function returning an escaping pointer, p requires storage surviving the call and the standard compiler normally heap-allocates it. Inlining can change the result at a particular call site. Use go build -gcflags=-m to inspect decisions; nonescaping values can still need heap storage for implementation reasons such as size.

Things that commonly force a value to escape in Go: returning its address, storing it in a global or a heap object, capturing it in a closure that outlives the call, or storing an interface value in an escaping location. Merely forming a pointer or interface does not universally force heap allocation.

## Key takeaways
- HotSpot escape analysis can eliminate an object allocation through scalar replacement; it does not promise to put every non-escaping object on a stack.
- Go can safely return a pointer to a local because its storage must survive the call; inlining changes particular allocation decisions.
- A pointer or interface value alone does not universally force Go heap allocation; inspect compiler diagnostics for the actual context.

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
