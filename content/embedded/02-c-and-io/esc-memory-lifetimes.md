---
id: esc-memory-lifetimes
title: Array bounds and object lifetimes
level: basic
minutes: 4
summary: Keep storage alive for every pointer use and pass a buffer capacity explicitly.
---

A pointer can refer to the correct kind of object and still be unsafe to use. Two further questions matter: is that object still alive, and is the requested element inside its bounds? C generally leaves these checks to the program.

## A local array belongs to its scope

An ordinary local array has **automatic storage duration**. Its lifetime ends when execution leaves its enclosing block. Returning a pointer to that local array does not keep the array alive. Reading or writing the former object afterwards has undefined behaviour: the language does not promise an outcome, even if one test appears to work.

An object declared with **static storage duration** lasts for the execution of the program. That does not mean it is non-volatile storage or that its contents survive a reset. Static objects can also introduce shared state, so they are not an automatic replacement for a clear ownership contract.

> [!analogy] Real-world analogy: a key to a borrowed workbench
> Keeping the key to a borrowed workbench does not extend your booking. You need both the key and permission to use the bench at that time.
>
> **How it maps:** A pointer alone does not extend an object's lifetime. The caller must know who owns the storage and how long it remains available.
>
> **Where it stops:** C does not check the booking for every access. A stale pointer can cause undefined behaviour rather than a helpful refusal.

## Let the caller provide the storage

This complete C11 host example writes three readings into an array supplied by its caller. `size_t` is an unsigned type suitable for object sizes and array counts. `NULL` is a null pointer constant; the function rejects it here before dereferencing.

```c
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

size_t fill(uint16_t *out, size_t cap) {
    if (out == NULL || cap < 3u)
        return 0u;
    out[0] = 10u;
    out[1] = 20u;
    out[2] = 30u;
    return 3u;
}

int main(void) {
    uint16_t samples[3] = {0u};
    size_t count = fill(samples, 3u);
    printf("%u %u\n", (unsigned)count,
           (unsigned)samples[2]);
    return 0;
}
```

It prints `3 30`. The array's valid indexes are 0, 1 and 2. Index 3 is one past its end and cannot be dereferenced. Passing an array to this function supplies a pointer to its first element, not a copy of the whole array or its capacity. The separate `cap` parameter records the caller's promise about writable elements.

The check is useful but cannot discover whether that promise is true: a non-null pointer and a large claimed capacity do not prove a valid buffer exists. The caller must supply a live writable array of at least that capacity. In this example the caller's own array remains alive for the whole call and subsequent print.

## Prefer explicit ownership before allocation tricks

For a small controller, fixed buffers with documented owners often make memory use easier to reason about. They still require bounds checks. Dynamic allocation has additional ownership and failure handling, but it is not needed for this beginner example. Decide who may change each buffer, when it may be reused and whether another context can still be using it.

## Key takeaways
- A pointer does not extend the lifetime of its object.
- Pass buffer capacity and return how much valid data was produced.
- Bounds checks depend on an honest caller contract as well as checks on each array index.

## Further reading
- [C11 draft: object lifetime, arrays and pointer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
