---
id: gc-manual-memory
title: Manual memory and its bugs
level: basic
minutes: 12
summary: The malloc/free contract seen from the programmer's side, the five classic bugs it invites, why they become security holes, and the tools and disciplines (ownership rules, RAII, arenas, sanitizers) that tame them.
---

In C, heap memory has exactly the lifetime you give it. You ask for a block with `malloc`, and it stays allocated until you hand it back with `free`. Nothing checks your work.

That is wonderfully simple and fast, and it is the root of a large share of the world's security vulnerabilities. This lesson looks at the contract, the ways it breaks, and the techniques programmers use so that it breaks less often.

## The contract

```c
#include <stdlib.h>

int *a = malloc(10 * sizeof *a);
if (a == NULL) { abort(); }
/* ... use a[0] .. a[9] ... */
free(a);
a = NULL;   /* defensive */
```

The rules are short:

1. Release each owned allocation once when no longer needed, either with free or by a successful realloc that replaces its lifetime. Do not separately free the old pointer after successful realloc; on failure for a nonzero requested size, the original allocation remains valid.
2. After `free`, the block is **not yours**: do not read it, write it or free it again.
3. Only touch bytes **inside** the block you were given.
4. `malloc` does not initialise memory; `calloc` zeroes it.

The language enforces none of these. Breaking any of them is either a **leak** (wasted memory) or **undefined behaviour** (anything can happen, including appearing to work).

## Who frees it? Ownership by convention

The real difficulty is not calling `free`; it is knowing **who** should call it and **when**. A pointer in C says nothing about whether you own the memory. That information lives only in documentation and habit.

```c
/* Requires valid NUL-terminated who. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Caller owns result; free if non-NULL. */
char *greet(const char *who) {
    /* "Hello, " (7) + name + NUL (1) */
    size_t n = strlen(who) + 8;
    char *s = malloc(n);
    if (!s) return NULL;
    snprintf(s, n, "Hello, %s", who);
    return s;
}
```

Compare `getenv`, whose result you must **not** free, and `strdup`, whose result you **must** free. Both return `char *`. Getting the convention wrong in either direction is a bug.

> [!tip] Counting bytes for strings
> `"Hello, "` is 7 characters. A C string also needs a terminating NUL byte, so the buffer must be `strlen(who) + 7 + 1`. Forgetting the `+ 1` is one of the most common heap overflows.

## The five classic bugs

### 1. Memory leak

Memory that is never freed, typically because the last pointer to it was lost.

```c
void handle(void) {
    char *buf = malloc(4096);
    if (!buf) return;
    /* Fill buf before parsing. */
    if (parse(buf) < 0)
        return;          /* leak: no free */
    free(buf);
}
```

An ordinary process exit reclaims its address space, so a small bounded leak in a short-lived tool may have limited impact. In an illustrative server, leaking 4,000 bytes per request at 1,000 requests/s accumulates 345.6 GB per day (decimal). The time and mode of failure depend on memory limits, allocation behavior and the environment; an OOM kill within hours is not guaranteed.

### 2. Use-after-free

Reading or writing a block after it has been freed. The pointer still holds the old address (a **dangling pointer**), and the allocator may already have given that memory to someone else.

```c
struct user *u = find_user(id);
free(u);
log_access(u->name);  /* use-after-free */
```

### 3. Double free

Calling `free` twice on the same block. This is undefined behavior. An allocator may detect and abort, or corruption and later exploitation may result; no specific allocator outcome is guaranteed.

### 4. Buffer overflow

Writing past the end (or before the start) of a block, trampling the allocator's metadata or a neighbouring object.

```c
char *s = malloc(strlen(src));  /* no +1 */
strcpy(s, src);   /* writes NUL past end */
```

### 5. Uninitialised read

Using `malloc`'d memory before writing it. Its contents are indeterminate; stale bytes can cause information disclosure, and reading an uninitialized typed value can invoke undefined behavior. Fresh pages may happen to be zero-filled, but malloc does not promise initialization.

| Bug | Symptom | Danger |
|---|---|---|
| Leak | memory grows | outage |
| Use-after-free | random corruption | exploit |
| Double free | allocator crash | exploit |
| Overflow | corruption | exploit |
| Uninit read | odd values | info leak |

## Why these are security holes

These bugs are not just crashes. Consider a use-after-free:

1. The program frees an object that contains a function pointer, but keeps a dangling pointer to it.
2. An attacker triggers an allocation of the same size with contents they control (say, a string from a network packet). The allocator reuses the freed slot.
3. The program calls through its dangling pointer, reading the attacker's bytes as a function address.

If the slot is reused as assumed and control-flow defenses do not stop the indirect call, this can enable arbitrary code execution. Overflows and double frees can be turned into similar primitives.

Chromium’s published analysis reported roughly 70% of its high-severity security bugs as memory-safety issues, with use-after-free a major category. Treat this as the historical dataset described by the source, not a measured current rate across all products. A separate universal Microsoft annual percentage is omitted here because this review has not established its applicable period and dataset. This is why governments and large companies now push new code towards **memory-safe languages**: Java, Go, Python, C#, Swift and Rust.

> [!note] What "memory safe" means
> A memory-safe language guarantees you cannot read or write memory you do not own: no dangling pointers, no out-of-bounds access, no double free. GC languages achieve it by never freeing reachable memory and bounds-checking arrays. Rust combines static ownership checks with runtime checks such as bounds checks and library synchronization (lesson 6); unsafe code and native interfaces remain obligations in all these systems.

## Disciplines that help in C

### Single exit and cleanup

```c
int process(const char *path) {
    int rc = -1;
    char *buf = NULL;
    FILE *f = fopen(path, "r");
    if (!f) goto out;
    buf = malloc(4096);
    if (!buf) goto out;
    /* ... work ... */
    rc = 0;
out:
    free(buf);        /* free(NULL) is OK */
    if (f) fclose(f);
    return rc;
}
```

Every path runs the same cleanup. The Linux kernel uses this `goto` pattern everywhere. Note that `free(NULL)` is defined to do nothing, which keeps this tidy.

### Arenas (region allocation)

Instead of freeing objects one by one, allocate everything for one task (a request, a compiler pass, a game frame) from an **arena** and free the whole arena at the end. Individual frees disappear, so most use-after-free and double-free bugs within that region disappear too. Compilers, game engines and web servers (nginx's per-request pools) use this heavily.

## C++: tie memory to object lifetime (RAII)

C++ keeps manual memory but automates the `free`. **RAII** (resource acquisition is initialisation) means a resource is owned by an object, and the object's **destructor** releases it when the object goes out of scope, on normal scope exit and exception unwinding. Process abort, termination and deliberately leaked ownership do not promise destructor execution.

```cpp
#include <memory>
#include <vector>

void f() {
    auto p = std::make_unique<Widget>();
    std::vector<int> v(1000);
    // ... may throw ...
}   // ~vector and ~unique_ptr run here
```

- `std::unique_ptr<T>`: exactly one owner; cannot be copied, only moved. Often pointer-sized with the default deleter; a stateful deleter or custom pointer type can change representation and cost.
- `std::shared_ptr<T>`: shared ownership via reference counting (lesson 3).

RAII removes most leaks and double frees. It does not stop use-after-free through raw pointers or references that outlive the owner. Rust's borrow checker is, in effect, RAII plus a compiler that proves those references cannot dangle.

## Garbage collection is not a cure for leaks

GC languages free memory only when it becomes **unreachable**. If your program keeps a reference, the memory stays, even if you will never use it again. These are logical leaks:

```python
_cache = {}

def get_report(user_id, day):
    key = (user_id, day)
    if key not in _cache:
        _cache[key] = build_report(
            user_id, day)
    return _cache[key]   # grows forever
```

Common culprits in Python, Java and Go: unbounded caches and maps, listeners or callbacks that are registered and never removed, static collections, and (in Go) goroutines blocked forever on a channel, which pin everything they reference.

GC also does not manage **other resources**. Files, sockets and locks must still be released deterministically:

| Language | Mechanism |
|---|---|
| Python | `with open(...) as f:` |
| Java | try-with-resources |
| Go | `defer f.Close()` |
| C++ / Rust | destructor / `Drop` |

## Finding the bugs

- **AddressSanitizer** (`-fsanitize=address` in Clang and GCC) instruments relevant memory accesses in compiled code; uninstrumented code and other coverage limitations remain. It reports heap-use-after-free, buffer overflows and double frees with stack traces, with a typical slowdown of about 2x, so you can run your test suite under it.
- **Valgrind Memcheck** runs an unmodified binary on a simulated CPU. No recompilation, but programs run roughly 20 to 30 times slower.
- **LeakSanitizer** and Valgrind's `--leak-check=yes` report blocks still allocated at exit with no pointer to them.
- **Fuzzers** (libFuzzer, AFL) combined with sanitizers find the inputs that trigger these bugs.

These find bugs in the code paths you exercise. They cannot prove their absence, which is the gap memory-safe languages close.

## Key takeaways
- `malloc` and `free` give exact, fast control; the language checks none of the rules.
- Ownership in C is a convention in documentation, which is why "who frees this?" causes so many bugs.
- The classic bugs are leaks, use-after-free, double free, buffer overflow and uninitialised reads; the last four are routinely exploitable.
- Chromium’s cited historical analysis attributed around 70% of its high-severity bugs to memory-safety issues; this is not a universal current rate.
- RAII, `unique_ptr`, arenas and cleanup patterns reduce bugs; sanitizers and Valgrind find them in tested paths.
- Garbage collection prevents dangling pointers but not logical leaks, and does not close files or sockets for you.

## Further reading
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Valgrind quick start guide](https://valgrind.org/docs/manual/quick-start.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [Resource acquisition is initialization — Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
- [Region-based memory management — Wikipedia](https://en.wikipedia.org/wiki/Region-based_memory_management)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 5](https://eel.is/c++draft/unique.ptr.single)
