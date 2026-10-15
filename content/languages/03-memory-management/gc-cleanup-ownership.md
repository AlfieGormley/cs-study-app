---
id: gc-cleanup-ownership
title: "Cleanup paths, arenas and RAII"
level: basic
minutes: 3
sourceLesson: gc-manual-memory
summary: "A cleanup label can release every resource acquired before any failure, and free(NULL) needs no special case"
---

Once ownership is explicit, arrange for release to follow one dependable lifetime boundary. C uses conventions and cleanup paths; arenas and C++ resource-owning objects reduce the number of individual decisions.

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
/* Both success and failure arrive here. */
out:
    free(buf);        /* free(NULL) is OK */
    if (f) fclose(f);
    return rc;
}
```

Every path runs the same cleanup. The Linux kernel uses this `goto` pattern everywhere. Note that `free(NULL)` is defined to do nothing, which keeps this tidy.

### Arenas (region allocation)

Instead of freeing objects one by one, allocate everything for one task (a request, a compiler pass, a game frame) from an **arena allocator** and free the whole arena at the end. Individual frees disappear, removing many per-object release mistakes. Pointers that outlive arena release still dangle, and oversized retention until arena teardown can waste memory. Compilers, game engines and web servers (nginx's per-request pools) use this heavily.

## C++: tie memory to object lifetime (RAII)

C++ keeps manual memory but automates the `free`. **RAII** (resource acquisition is initialisation) means a resource is owned by an object, and the object's **destructor** releases it when the object goes out of scope, on normal scope exit and exception unwinding. Process abort, termination and deliberately leaked ownership do not promise destructor execution.

```cpp
#include <memory>
#include <vector>

void f() {
    auto p = std::make_unique<Widget>();
    // Its owner also cleans up on
    // unwinding.
    std::vector<int> v(1000);
    // ... may throw ...
}   // ~vector and ~unique_ptr run here
```

- `std::unique_ptr<T>`: exactly one owner; cannot be copied, only moved. Often pointer-sized with the default deleter; a stateful deleter or custom pointer type can change representation and cost.
- `std::shared_ptr<T>`: shared ownership via reference counting.

Correctly designed resource-owning RAII types prevent many forgotten releases and duplicate releases. It does not stop use-after-free through raw pointers or references that outlive the owner. Rust's borrow checker is, in effect, RAII plus a compiler that proves those references cannot dangle.

## Key takeaways
- A cleanup label can release every resource acquired before any failure, and free(NULL) needs no special case.
- An arena is useful when many objects share one bounded task lifetime; references must not escape beyond arena release.
- RAII releases owned resources during normal scope exit and exception unwinding, while raw dangling references and termination paths remain separate concerns.

## Further reading
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Valgrind quick start guide](https://valgrind.org/docs/manual/quick-start.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [Resource acquisition is initialization — Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
- [Region-based memory management — Wikipedia](https://en.wikipedia.org/wiki/Region-based_memory_management)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 5](https://eel.is/c++draft/unique.ptr.single)
