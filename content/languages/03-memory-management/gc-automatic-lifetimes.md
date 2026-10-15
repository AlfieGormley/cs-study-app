---
id: gc-automatic-lifetimes
title: "Automatic lifetimes and Python references"
level: basic
minutes: 4
sourceLesson: gc-stack-heap
summary: "A pointer to an expired C automatic object cannot safely be dereferenced, regardless of the output in a quick experiment"
---

A returned pointer must still designate a live object. C makes the programmer obey storage-duration rules; Python names instead refer to managed objects. The same assignment spelling can therefore have very different consequences.

## The classic bug: returning a stack address

C distinguishes storage durations; it does not require a physical stack. Automatic locals commonly use frames or registers, static locals use static storage, and malloc obtains allocated storage.

```c
#include <stdlib.h>

/* Return does not extend x's lifetime. */
int *bad(void) {
    int x = 42;
    return &x;   /* frame dies here */
}

int *good(void) {
    int *p = malloc(sizeof *p);
    /* Allocation failure transfers
     * nothing. */
    if (!p) return NULL;
    *p = 42;
    return p;    /* caller must free */
}
```

`bad` returns a pointer to an automatic object whose lifetime has ended; a conventional stack frame is only the implementation model. Accessing the expired object is undefined behaviour regardless of whether later calls reuse that storage; no particular output or crash is guaranteed. Clang warns: *address of stack memory associated with local variable 'x' returned*. `good` returns NULL on allocation failure; on success the caller has a new duty: call `free(p)` once and only once.

## Python: names reference managed objects

CPython represents values as objects with type and reference-management metadata. Most are dynamically allocated; some singleton/static objects and immortal objects are exceptions, and free-threaded builds have different counting details. Some objects, such as `None` and cached small integers, are shared rather than freshly allocated for each use; exact creation and caching details belong to the CPython implementation. A local variable is just a name in the frame that **refers** to an object.

```python
# The returned reference keeps the list
# alive.
def make():
    xs = [1, 2, 3]   # list object on heap
    return xs        # return the reference

a = make()       # list survives the call
```

The list survives this call because `a` still refers to it. That is why "stack vs heap" rarely comes up in Python: you never place anything yourself, and the runtime manages reclamation; cycles and finalization complicate promptness.

## Value and reference semantics

Placement is tied to what assignment means:

- **Value semantics**: assignment copies the data. C structs, Go structs and arrays, and Rust's `Copy` types behave this way.
- **Reference semantics**: assignment copies a pointer, so two names share one object. Python objects and Java objects behave this way.

```python
a = [1, 2]
b = a          # same list, not a copy
# Mutate the shared list through b.
b.append(3)
print(a)       # [1, 2, 3]
```

The list cannot be reclaimed while either name still strongly retains it. Other aliases can retain it too, so reclamation must account for every strong path, not only these two names.

## Key takeaways
- A pointer to an expired C automatic object cannot safely be dereferenced, regardless of the output in a quick experiment.
- CPython names refer to managed objects; retaining the returned list keeps that list alive.
- Assigning a Python list to another name shares the list rather than copying it.

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
