---
id: gc-manual-bug-patterns
title: "Five manual-memory failure patterns"
level: basic
minutes: 4
sourceLesson: gc-manual-memory
summary: "Leaks retain allocations; use-after-free, double free, out-of-bounds writes and uninitialised reads violate separate rules"
---

Before choosing a tool or a repair, identify which allocation rule failed. These examples deliberately contain bugs; their invalid accesses have no guaranteed output.

## The five classic bugs

### 1. Memory leak

Memory that is never freed, typically because the last pointer to it was lost.

```c
void handle(void) {
    char *buf = malloc(4096);
    if (!buf) return;
    /* Fill buf before parsing. */
    /* Failure bypasses the release
     * below. */
    if (parse(buf) < 0)
        return;          /* leak: no free */
    free(buf);
}
```

An ordinary process exit reclaims its address space, so a small bounded leak in a short-lived tool may have limited impact. In an illustrative server, leaking 4,000 bytes per request at 1,000 requests/s accumulates 345.6 GB per day (decimal). The time and mode of failure depend on memory limits, allocation behavior and the environment; an OOM kill within hours is not guaranteed.

The daily figure is the leak rate multiplied by the number of seconds in a day:

```formula
R = 4,000 B/req × 1,000 req/s
R = 4,000,000 B/s
D = R × 86,400 s
D = 345,600,000,000 B = 345.6 GB
where
R: the leak rate: bytes lost per second
B: bytes
req: one request handled by the server
s: seconds
D: the memory leaked in one day, in bytes
86,400: the number of seconds in a day (24 × 60 × 60)
GB: gigabyte, 1,000,000,000 bytes (decimal)
In words: 4 kB lost on each of 1,000 requests a second is 4 MB a second, which over a day adds up to about 346 GB.
```

The model assumes a steady request rate and that nothing frees the leaked memory; real traffic varies through the day, so treat it as an order-of-magnitude warning, not a prediction.

### 2. Use-after-free

Reading or writing a block after it has been freed. The pointer still holds the old address (a **dangling pointer**), and the allocator may already have given that memory to someone else.

```c
struct user *u = find_user(id);
/* u becomes invalid for object access. */
free(u);
log_access(u->name);  /* use-after-free */
```

### 3. Double free

Calling `free` twice on the same block. This is undefined behavior. An allocator may detect and abort, or corruption and later exploitation may result; no specific allocator outcome is guaranteed.

### 4. Buffer overflow

Writing past the end (or before the start) of a block, trampling the allocator's metadata or a neighbouring object.

```c
char *s = malloc(strlen(src));  /* no +1 */
/* Copy includes the missing NUL byte. */
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

## Key takeaways
- Leaks retain allocations; use-after-free, double free, out-of-bounds writes and uninitialised reads violate separate rules.
- A dangling pointer is not made safe by an allocator leaving familiar bytes behind.
- A steady leak-rate calculation is a sizing model, not a prediction of the exact time or mode of process failure.

## Further reading
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Valgrind quick start guide](https://valgrind.org/docs/manual/quick-start.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [Resource acquisition is initialization — Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
- [Region-based memory management — Wikipedia](https://en.wikipedia.org/wiki/Region-based_memory_management)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 5](https://eel.is/c++draft/unique.ptr.single)
