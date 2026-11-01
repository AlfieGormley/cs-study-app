---
id: sys-object-ownership
title: Lifetimes, stale aliases and ownership
level: intermediate
minutes: 5
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

> [!analogy] Real-world analogy: a hotel key that still opens the old room
> You check out of a hotel but keep your key card. If the hotel forgot to re-code the lock, the card still opens room 412, which now holds the next guest's luggage.
>
> **How it maps:** The room is a block of heap storage, checking out is `free`, the next guest is a new allocation that reuses the storage, and the kept key card is a dangling pointer. Reading `s->is_admin` is opening the door and trusting whatever is now inside.
>
> **Where it stops:** A hotel can re-code every lock at checkout; C's `free` does nothing to the pointers you still hold, and nothing announces that the room has a new occupant. Whether and when storage is reused is up to the allocator, and the invalid access has undefined behaviour rather than a predictable result.

Defences in C:

- After `free`, setting an owning pointer to `NULL` can support later explicit null checks and makes `free(NULL)` harmless. Dereferencing NULL is still undefined behaviour, not a guaranteed clean crash; other aliases still dangle.
- Give every allocation **one clear owner** responsible for freeing it, and document which functions borrow versus take ownership.
- In C++, prefer `std::unique_ptr` when one owner holds the object, using `std::shared_ptr` when ownership really is shared. Raw borrowed aliases and unsynchronised access still require lifetime discipline.

An AddressSanitizer test build can catch many accesses while released storage remains poisoned. An access after that address has been reused for a live allocation may escape this check; the underlying lifetime error still needs repair.

### Double free

Freeing the same allocation twice is undefined behaviour; `free(NULL)` is exempt. Outcomes can include allocator corruption or a diagnostic abort. Whether a double free is detected is implementation-dependent, and detecting it does not make double free safe. Clear ownership and avoiding stale aliases prevent the underlying error.

## What a memory-safe language changes

C and C++ leave both questions, "is this index inside the object?" and "is this object still alive?", to the programmer. A **memory-safe language** answers them in the language itself:

- **Bounds are checked.** In Java, an array index below zero or at least the array's length throws `ArrayIndexOutOfBoundsException`. In Rust, indexing a vector past its end causes a Rust panic, and `v.get(i)` returns `None` for the code to handle. Either way the neighbouring bytes are never read or written.
- **Lifetimes are enforced.** Java programs never free objects explicitly: a garbage collector reclaims only objects that nothing can still reach, so a reference that still exists keeps its object alive instead of pointing into reused storage. Safe Rust has no garbage collector: its ownership rules and **borrow checker** reject, at compile time, code that uses a value after it has been moved or dropped, keeps a reference longer than the value lives, or would free it twice.

So spatial and temporal bugs no longer corrupt memory without warning. They become a compile-time error or a defined, contained failure. That is why, in December 2023, CISA, NSA, the FBI and partner agencies in Australia, Canada, the UK and New Zealand urged software makers to publish **memory-safe roadmaps** for moving to memory-safe languages, and why CISA and NSA repeated the case in joint guidance in June 2025.

What it does not remove:

- **Unchecked code.** In unsafe Rust (code inside an `unsafe` block), the programmer can dereference raw pointers and call C functions through a foreign function interface (FFI); the compiler does not check those operations for memory safety. Bugs in linked C or C++ libraries remain.
- **Crashes.** A panic or exception is still an availability failure if nothing handles it.
- **Other bug classes.** Logic and authorisation errors remain. Ported to Java, the session example above would no longer read reused memory: the stale reference keeps the old, expired session alive, and the code could still grant access to it. The missing "is this session still valid?" check is a logic bug. The 2023 roadmap guidance itself notes that memory-safe languages are not free from other critical vulnerabilities.

## Key takeaways
- Freeing an allocation ends its lifetime; an address remaining mapped does not keep the object alive.
- Nulling one owning pointer does not repair other aliases.
- Clear ownership and disciplined borrowing address the cause of use-after-free and double free.
- Memory-safe languages turn bounds and lifetime errors into compile errors or defined failures; `unsafe` code, foreign libraries and logic bugs remain.

## Further reading
- [AddressSanitizer — Clang](https://clang.llvm.org/docs/AddressSanitizer.html)
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [CWE-416: use after free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [The Case for Memory Safe Roadmaps — CISA and partners](https://www.cisa.gov/resources-tools/resources/case-memory-safe-roadmaps)
- [What is ownership? — The Rust Programming Language](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
