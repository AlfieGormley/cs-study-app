---
id: sys-object-ownership
title: Lifetimes, stale aliases and ownership
level: intermediate
minutes: 3
sourceLesson: sys-memory-bugs
summary: Freeing an allocation ends its lifetime; an address remaining mapped does not keep the object alive.
---

## Use-after-free

A **use-after-free** (UAF) is a temporal bug: the program keeps using a pointer after the memory it points to has been released.

```c
struct session *s = load_session();
/* The owning pointer is not cleared. */
if (expired(s))
    free(s);
/* ... later, on another path ... */
/* BUG: the old object may be gone. */
if (s->is_admin)
    grant_access();
```

An allocator may reuse freed storage for a later allocation. If request-controlled bytes occupy that storage, a dangling access can influence an authorisation decision or a control pointer. Reuse timing is allocator-dependent, and undefined behaviour means no particular result is guaranteed. The fragment assumes `load_session` succeeded; real code must also handle failure.

Defences in C:

- After `free`, setting an owning pointer to `NULL` can support later explicit null checks and makes `free(NULL)` harmless. Dereferencing NULL is still undefined behaviour, not a guaranteed clean crash; other aliases still dangle.
- Give every allocation **one clear owner** responsible for freeing it, and document which functions borrow versus take ownership.
- In C++, prefer `std::unique_ptr` when one owner holds the object, using `std::shared_ptr` when ownership really is shared. Raw borrowed aliases and unsynchronised access still require lifetime discipline.

An AddressSanitizer test build can catch many accesses while released storage remains poisoned. An access after that address has been reused for a live allocation may escape this check; the underlying lifetime error still needs repair.

### Double free

Freeing the same allocation twice is undefined behaviour; `free(NULL)` is exempt. Outcomes can include allocator corruption or a diagnostic abort. Whether a double free is detected is implementation-dependent, and detecting it does not make double free safe. Clear ownership and avoiding stale aliases prevent the underlying error.

## Key takeaways
- Freeing an allocation ends its lifetime; an address remaining mapped does not keep the object alive.
- Nulling one owning pointer does not repair other aliases.
- Clear ownership and disciplined borrowing address the cause of use-after-free and double free.

## Further reading
- [AddressSanitizer — Clang](https://clang.llvm.org/docs/AddressSanitizer.html)
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [CWE-416: use after free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
