---
id: sync-race-conditions-data-races
title: Data races and check-then-act
level: basic
minutes: 3
summary: Separate undefined C data races from higher-level races in individually locked operations.
sourceLesson: sync-race-conditions
---

## Data races versus race conditions

These two terms are often used interchangeably, but they mean different things.

A **data race** is a precise, language-level definition. In C and C++ it is two accesses to the same memory location, from different threads, where the accesses conflict (for example, at least one writes), at least one is non-atomic, and neither happens before the other (no lock, no other synchronisation). In C and C++ a data race is **undefined behaviour**: the compiler may assume it never happens.

A **race condition** is a broader, semantic bug: the program's correctness depends on the relative timing of events.

| | Data race | No data race |
|---|---|---|
| Race condition | `counter++` unlocked | check-then-act |
| No race condition | rare, still UB in C | correct code |

The interesting cell is "race condition without a data race". Every individual access can be protected and the program can still be wrong:

```python
# each call takes the lock internally
if account.balance() >= 100:
    # Another thread can pass the same
    # check.
    account.withdraw(100)
```

Two threads can both see a balance of 150, both pass the check, and both withdraw. Each method is thread-safe; the *combination* is not. This pattern is called **check-then-act** (or time-of-check to time-of-use, TOCTOU), and it is also a classic security bug with files: checking permissions on a path, then opening it after an attacker has replaced it with a symlink.

The fix is to make the check and the action a single atomic unit: hold one lock across both, or offer an operation like `withdraw_if_at_least(100)`.

## Where races hide in real systems

- **Lazy initialisation**: two threads both see `cache is None` and both build it, or worse, one sees a half-built object.
- **Statistics counters** shared by worker threads.
- **Collections**: appending to a C++ `std::vector` or a Java `HashMap` from several threads can corrupt the structure itself, not just lose a value.
- **Files and databases**: two processes read-modify-write the same row or file. The same lost-update anomaly appears in databases, where it is handled by transactions and isolation levels.

Tools help find them. ThreadSanitizer (`-fsanitize=thread` in GCC and Clang) detects data races at run time; Helgrind (Valgrind) does similar. Neither finds check-then-act bugs where every access is locked.

## Key takeaways

- A C/C++ data race involves conflicting accesses not ordered by happens-before, with at least one non-atomic access.
- Individually locked methods can still form an incorrect check-then-act sequence.
- Race detectors inspect executed memory accesses; they do not prove application invariants.

## Further reading

- [OSTEP: Concurrency, an introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [C11 draft: memory model and atomics](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [ThreadSanitizer documentation](https://clang.llvm.org/docs/ThreadSanitizer.html)
