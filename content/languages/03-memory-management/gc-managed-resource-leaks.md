---
id: gc-managed-resource-leaks
title: "Reachability leaks and resource cleanup"
level: basic
minutes: 3
sourceLesson: gc-manual-memory
summary: "Reachable but obsolete cache entries cannot be identified as unnecessary by ordinary reachability collection"
---

A collector answers whether an object is reachable, not whether retaining it still serves the application. Memory retention and resource release therefore remain design responsibilities even in a managed language.

## Garbage collection is not a cure for leaks

GC languages free memory only when it becomes **unreachable**. If your program keeps a reference, the memory stays, even if you will never use it again. These are logical leaks:

```python
_cache = {}

def get_report(user_id, day):
    key = (user_id, day)
    # Each distinct key can retain a report.
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

## Bound the retention policy

For the report cache, specify an eviction or expiry rule as well as a lookup rule. A test can request many distinct user-and-day pairs and inspect whether obsolete entries leave the cache. A bounded cache may intentionally retain useful reports; indefinite retention without a useful policy is the logical leak.

A blocked goroutine can also retain values needed by its suspended computation. Arrange cancellation or a channel protocol that lets it return, rather than assuming a collector will terminate the goroutine. Exact retained bytes depend on compiler liveness and runtime representation.

Files and sockets use operating-system resources in addition to any small wrapper object. Closing them promptly avoids exhausting descriptors even when plenty of heap remains. Use the language's explicit cleanup construct and handle close errors where they matter, rather than relying on an unspecified finalizer schedule.

## Key takeaways
- Reachable but obsolete cache entries cannot be identified as unnecessary by ordinary reachability collection.
- Cancellation, listener removal and bounded cache policies control logical retention.
- Use with, try-with-resources, defer or documented destructor behaviour to release non-memory resources promptly.

## Further reading
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Valgrind quick start guide](https://valgrind.org/docs/manual/quick-start.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [Resource acquisition is initialization — Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
- [Region-based memory management — Wikipedia](https://en.wikipedia.org/wiki/Region-based_memory_management)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 5](https://eel.is/c++draft/unique.ptr.single)
