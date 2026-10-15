---
id: conc-rust-concurrency-limits
title: Data-race freedom and remaining logic bugs
level: advanced
minutes: 3
sourceLesson: conc-structured-rust
summary: Safe Rust still permits deadlocks, logic races and resource leaks.
---

Borrowing and Send/Sync prevent data races in sound safe Rust. They do not prove that a concurrent algorithm makes progress, uses bounded memory or performs a correct multi-step transaction.

### What Rust does not prevent

"Fearless concurrency" is about **data races**, not every concurrency bug:

- **Deadlock.** Two threads locking `a` then `b` and `b` then `a` compiles fine. Locking a `Mutex` twice on one thread deadlocks or panics.
- **Race conditions.** Reading a balance under one lock acquisition and writing it under another is a logic race, as in the earlier check-then-act examples. Each access is synchronised; the sequence is not.
- **Leaks.** An `Arc` cycle is never freed.
- **Atomics misuse.** Weak atomic orderings can give surprising results. Safe atomic operations do not themselves create data-race UB, but an unsafe abstraction that relies on incorrect publication or lifetime ordering can be unsound.
- **`unsafe` code.** `unsafe impl Send` is a promise the compiler cannot check.

One async subtlety: holding a `std::sync::MutexGuard` across an `.await` makes the whole future `!Send`, because `MutexGuard` is not `Send`. `tokio::spawn` then refuses it with "future cannot be sent between threads safely". The compiler is protecting you from a guard being released on a different thread from the one that took it.

## Putting the module together

| Model | Prevents data races by |
|---|---|
| Threads + locks | Discipline |
| Single-loop async | Serialized task execution, subject to re-entrancy and external threads |
| Go channels | Ownership discipline; sharing is still possible |
| Isolated actors | Private state; shared references/external stores need care |
| Rust | Type checking |

Structured concurrency is orthogonal: it can be layered on any of them (TaskGroup on async, scopes on threads, nurseries in Trio, `coroutineScope` on Kotlin's coroutines) and gives child lifetime and failure handling an explicit structure. It cannot force uncooperative work to finish or eliminate every resource leak.

## Key takeaways
- Safe Rust still permits deadlocks, logic races and resource leaks.
- A non-Send guard across await prevents spawning that future with tokio::spawn.

## Further reading
- [Notes on structured concurrency, or: Go statement considered harmful — Nathaniel J. Smith](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)
- [Coroutines and Tasks: Task Groups — Python docs](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [JEP 543: Structured Concurrency — OpenJDK](https://openjdk.org/jeps/543)
- [Coroutines basics — Kotlin docs](https://kotlinlang.org/docs/coroutines-basics.html)
- [Extensible Concurrency with Send and Sync — The Rust Programming Language](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html)
- [Send and Sync — The Rustonomicon](https://doc.rust-lang.org/nomicon/send-and-sync.html)
- [std::thread::scope — Rust docs](https://doc.rust-lang.org/std/thread/fn.scope.html)
- [Primary verification source 3](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
- [Primary verification source 4](https://doc.rust-lang.org/std/sync/struct.MutexGuard.html)
- [Primary verification source 7](https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html)
- [Primary verification source 8](https://kotlinlang.org/docs/composing-suspending-functions.html#structured-concurrency-with-async)
