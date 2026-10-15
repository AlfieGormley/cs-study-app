---
id: gc-allocation-contract
title: "The allocation and ownership contract"
level: basic
minutes: 4
sourceLesson: gc-manual-memory
summary: "An allocated C object remains valid until its lifetime ends through deallocation or successful reallocation"
---

C allocated storage lasts from successful allocation until its lifetime ends through deallocation or replacement by a successful realloc. The language relies on the programmer to follow the contract; warnings, static analysis and run-time tools can detect some violations.

That is wonderfully simple and fast, and it is the root of a large share of the world's security vulnerabilities. This lesson looks at the contract, the ways it breaks, and the techniques programmers use so that it breaks less often.

## The contract

```c
#include <stdlib.h>

int *a = malloc(10 * sizeof *a);
if (a == NULL) { abort(); }
/* ... use a[0] .. a[9] ... */
/* Release the allocation, not aliases. */
free(a);
a = NULL;   /* defensive */
```

The rules are short:

1. Release each owned allocation once when no longer needed, either with free or by a successful realloc that replaces its lifetime. Do not separately free the old pointer after successful realloc; on failure for a nonzero requested size, the original allocation remains valid.
2. After `free`, the block is **not yours**: do not read it, write it or free it again.
3. Only touch bytes **inside** the block you were given.
4. `malloc` does not initialise memory; `calloc` zeroes it.

C does not provide automatic enforcement of these rules. Losing an owned allocation can cause a **memory leak**; invalid accesses or deallocation can cause **undefined behaviour**, for which C requires no particular outcome. A leak alone need not be undefined behaviour.

## Who frees it? Ownership by convention

The real difficulty is not calling `free`; it is knowing **who** should call it and **when**. A pointer in C says nothing about whether you own the memory. That information lives only in documentation and habit.

```c
/* who: valid NUL-terminated string. */
/* Its byte length must allow adding 8. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Caller owns result; free if non-NULL. */
char *greet(const char *who) {
    /* "Hello, " (7) + name + NUL (1) */
    size_t n = strlen(who) + 8;
    char *s = malloc(n);
    if (!s) return NULL;
    /* Include room for the terminating
     * NUL. */
    snprintf(s, n, "Hello, %s", who);
    return s;
}
```

Compare `getenv`, whose result you must **not** free, and `strdup`, whose result you **must** free. Both return `char *`. Getting the convention wrong in either direction is a bug.

> [!tip] Counting bytes for strings
> `"Hello, "` is 7 characters. A C string also needs a terminating NUL byte, so the allocation must be `strlen(who) + 7 + 1`. Forgetting the `+ 1` is one of the most common heap overflows.

The allocation size for `greet` is the sum of its three parts:

```formula
n = L + 7 + 1
n = 3 + 7 + 1 = 11
where
n: the number of bytes to ask malloc for (the variable n in greet)
L: the byte length returned by strlen(who), excluding its terminating NUL; for the three-byte name "ann", the value is 3
7: seven bytes for the ASCII-compatible greeting prefix "Hello, ": five letters, a comma and a space
1: the single terminating NUL byte that marks where every C string ends
In words: the allocation needs room for the greeting, the name and one extra byte for the terminator.
```

So `greet("ann")` allocates 11 bytes: `Hello, ann` is 10 visible characters plus the NUL. The code writes this as `strlen(who) + 8`, folding the 7 and the 1 together. Count encoded bytes, not visible letters: UTF-8 text can use several bytes per character. The added greeting is seven bytes on the assumed ASCII-compatible encoding. For arbitrary untrusted lengths, check that adding eight cannot overflow size_t before allocating.

## Key takeaways
- An allocated C object remains valid until its lifetime ends through deallocation or successful reallocation.
- Document who owns each returned pointer: getenv does not transfer ownership, while a successful strdup does.
- A C string allocation must include every payload byte and its terminating NUL, with checked size arithmetic for untrusted lengths.

## Further reading
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Valgrind quick start guide](https://valgrind.org/docs/manual/quick-start.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [Resource acquisition is initialization — Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
- [Region-based memory management — Wikipedia](https://en.wikipedia.org/wiki/Region-based_memory_management)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 5](https://eel.is/c++draft/unique.ptr.single)
