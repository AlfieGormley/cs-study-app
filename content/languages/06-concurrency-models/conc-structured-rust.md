---
id: conc-structured-rust
title: Structured concurrency and Rust's data-race freedom
level: advanced
minutes: 15
summary: Two ideas that make concurrent code checkable - structured concurrency, where tasks cannot outlive the block that started them, and Rust's ownership rules plus Send and Sync, which turn data races into compile errors.
---

Every model so far has left two problems to the programmer's discipline. **Lifetimes**: a goroutine or `create_task` can outlive the code that started it, so tasks leak and errors vanish (lessons 2 and 4). **Sharing**: nothing stops two threads touching the same data unsafely (lesson 1), unless isolation rules or synchronization APIs prevent unsafe sharing.

This lesson covers two approaches to these problems. **Structured concurrency** ties every task's lifetime to a lexical block. **Rust** keeps shared memory but makes the compiler prove there are no data races.

## Structured concurrency

### The problem with "go"

In 2018 Nathaniel J. Smith, author of Python's Trio library, argued in *Go statement considered harmful* that `go f()`, `create_task`, `thread.start()` and friends are the `goto` of concurrency. Once you call one, control splits in two, and nothing in the code's shape says where the second path ends.

```
 unstructured            structured
   main                    main
    |---spawn--> task       |
    |              |        +--------+
    |  (returns)   |        | task 1 |
    x              |        | task 2 |
          still running...  +--------+
                            | both done
                            v
```

Dijkstra's argument against `goto` was that you could no longer reason about a block as a unit. Smith's point is the same: with unstructured spawns, you cannot know whether a function has finished its work when it returns, where an exception in a child goes, or how to cancel everything it started.

### The rule

Structured concurrency adds one rule: **a task may not outlive the scope that started it**. Concretely, a fail-fast task scope such as a Trio nursery or asyncio TaskGroup typically:

1. Waits for all its children before the block exits.
2. If a child has an ordinary failure, requests sibling cancellation and propagates failure to the parent; cancellation exceptions and supervisory policies have distinct rules.
3. If the parent is cancelled, cancels all children.

The call tree of tasks then mirrors the block structure of the code, just as it does for ordinary function calls.

### Python: TaskGroup

Python 3.11 added `asyncio.TaskGroup`, modelled on Trio's nurseries:

```python
import asyncio

async def boom():
    await asyncio.sleep(0.1)
    raise ValueError("bad")

async def slow():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("slow cancelled")
        raise

async def both():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(slow())
        tg.create_task(boom())

async def main():
    try:
        await both()
    except* ValueError as eg:
        print("caught", eg.exceptions)

asyncio.run(main())
```

After about 0.1 seconds this prints `slow cancelled`, then `caught (ValueError('bad'),)`. `boom` fails, the group cancels `slow` instead of letting it run for 10 seconds, waits for it to finish cancelling, and raises an **ExceptionGroup**, because several children can fail at once. `except*` (also new in 3.11) matches exceptions inside a group by type.

Compare `asyncio.gather`: by default, if one awaitable fails, `gather` raises that error but does not itself cancel the other awaitables. The caller may still retain their handles, and loop shutdown may later cancel them.

> [!tip] Re-raise CancelledError
> Cancellation requests delivery of CancelledError at the next opportunity; it does not pre-empt arbitrary blocking or CPU-bound code. If you catch it to clean up, re-raise it. Swallowing it can interfere with cancellation and delay group exit; the group still waits for its children.

### Other languages

- **Kotlin**: `coroutineScope { launch { ... } }` waits for its children and cancels them all if one fails. `supervisorScope` lets siblings survive a failure. `GlobalScope.launch` is the unstructured escape hatch, and is discouraged.
- **Swift**: `async let` and `withTaskGroup` are structured; `Task { }` is not.
- **Java**: `StructuredTaskScope`, designed for virtual threads. It has been a preview API since JDK 21 (re-previewed in each release up to JDK 27), and JEP 543 proposes finalising it in JDK 28.

```java
try (var scope =
       StructuredTaskScope.open()) {
  var user  = scope.fork(() -> findUser());
  var order = scope.fork(() -> getOrder());
  scope.join();  // throws if either failed
  return new Response(user.get(),
                      order.get());
}  // no subtask can outlive this block
```

## Rust: data races as type errors

### Aliasing XOR mutation

Rust's ownership rules were designed for memory safety, but they also rule out data races. At any moment a value can have **either**:

- shared references &T (which prevent ordinary mutation but can allow synchronized interior mutability), **or**
- exactly one mutable reference `&mut T`.

A data race needs two accesses to the same memory, at least one a write, at the same time. Borrowing plus Send/Sync rules prevent unsynchronized conflicting access in safe Rust, assuming sound unsafe implementations underneath:

```rust
let mut count = 0;
thread::scope(|s| {
    s.spawn(|| count += 1);
    s.spawn(|| count += 1);
});
// error[E0499]: cannot borrow `count`
// as mutable more than once at a time
```

### Send and Sync

The borrow checker alone does not know which *types* are safe to use across threads. Two marker traits carry that information:

- `T: Send` means a value of type `T` can be **moved** to another thread.
- `T: Sync` means a `&T` can be **shared** between threads. Formally, `T` is `Sync` exactly when `&T` is `Send`.

They are **auto traits**: the compiler implements them for a struct automatically when all its fields have them. Most types are both. The interesting ones are the exceptions:

| Type | Send | Sync |
|---|---|---|
| `Rc<T>` | Never | Never |
| `Arc<T>` | If `T: Send + Sync` | Same |
| `RefCell<T>` | If `T: Send` | Never |
| `Mutex<T>` | If `T: Send` | If `T: Send` |
| `MutexGuard<T>` | Never | If `T: Sync` |

- `Rc` updates its reference count without atomic instructions; `Arc` uses atomic ones.
- `RefCell` tracks borrows at run time with a plain counter, so two threads sharing one could both "borrow mutably".
- Mutex<T> is Sync when T is Send, even if T is not Sync, because the lock ensures only one thread reaches the `T` at a time.
- A `MutexGuard` must be dropped (unlocking the mutex) on the thread that locked it, so it cannot be sent away.

`thread::spawn` requires its closure to be `Send + 'static`, so the compiler checks every captured value:

```rust
let a = Rc::new(5);
let b = Rc::clone(&a);
thread::spawn(move || {
    println!("{b}");
});
// error[E0277]: `Rc<i32>` cannot be
// sent between threads safely
```

If this compiled, both threads could bump the non-atomic refcount at once, lose an update, and free the value while it was still in use. Swapping `Rc` for `Arc` fixes it at the cost of atomic increments.

### Shared mutable state, checked

To mutate shared data you combine `Arc` (shared ownership) with `Mutex` (exclusive access):

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let c = Arc::new(Mutex::new(0));
    let mut hs = vec![];
    for _ in 0..4 {
        let c = Arc::clone(&c);
        hs.push(thread::spawn(move || {
            for _ in 0..1000 {
                *c.lock().unwrap() += 1;
            }
        }));
    }
    for h in hs { h.join().unwrap(); }
    println!("{}", *c.lock().unwrap());
}
// prints 4000
```

Compare lesson 1. There the lock and the counter were separate variables, linked only by convention. Here the counter lives **inside** the `Mutex`, and concurrent shared access uses a lock guard; exclusive access to the mutex itself also permits safe get_mut or consuming into_inner without locking. Forgetting the lock is not a bug you can write. The lock is released when the guard is dropped, at the end of the statement here.

`lock()` returns a `Result` because of **poisoning**: if poisoning detects an unwinding panic while the guard is held, later lock calls return a poison error unless it is cleared; detection is advisory and has exceptions, warning that the data may be half-updated.

### Scoped threads: structure meets borrowing

`thread::spawn` needs `'static` because the new thread might outlive the current function, so it cannot borrow locals. **Scoped threads**, stable since Rust 1.63, are structured concurrency for threads: every thread spawned in the scope is joined before `scope` returns, so borrowing is safe.

```rust
let v = vec![1, 2, 3, 4];
let (l, r) = v.split_at(2);
let mut a: i32 = 0;
let mut b: i32 = 0;
thread::scope(|s| {
    s.spawn(|| a = l.iter().sum());
    s.spawn(|| b = r.iter().sum());
}); // both threads joined here
println!("{a} {b} {v:?}");
// 3 7 [1, 2, 3, 4]
```

The compiler checks the borrows exactly as for ordinary code: each thread has shared borrows of a different half of `v` and the only mutable borrow of its own result variable. Point both threads at `a` and it is the E0499 error from earlier. Structured lifetimes permit these non-static borrows; unscoped threads are also checked, with stricter lifetime requirements.

Async Rust is less settled. `tokio::spawn` requires `'static + Send` futures, like `thread::spawn`. A sound "scoped spawn" for async is hard because a future can be dropped or leaked (`mem::forget` is safe Rust) without running to completion, so nothing guarantees the scope waits. Crates like `tokio::task::JoinSet` give partial structure: dropping the set requests task abortion but does not await cleanup; already-running spawn_blocking tasks cannot generally be aborted.

### What Rust does not prevent

"Fearless concurrency" is about **data races**, not every concurrency bug:

- **Deadlock.** Two threads locking `a` then `b` and `b` then `a` compiles fine. Locking a `Mutex` twice on one thread deadlocks or panics.
- **Race conditions.** Reading a balance under one lock acquisition and writing it under another is a logic race, as in lesson 2. Each access is synchronised; the sequence is not.
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
- Structured concurrency: tasks cannot outlive their scope. The scope waits for children, cancels siblings on failure and propagates errors.
- Python 3.11's `TaskGroup` raises an `ExceptionGroup` (caught with `except*`); `gather` can leave tasks running after an error.
- Java's StructuredTaskScope has been in preview since JDK 21; JEP 543, checked on 2026-10-05, proposes finalization for JDK 28; Kotlin and Swift have structured scopes built in.
- Rust: aliasing XOR mutation, plus `Send` (can move to a thread) and `Sync` (`&T` is `Send`), make data races a compile error.
- Rc is not Send or Sync; RefCell can be moved when its contents are Send but cannot be shared as Sync; `Arc<Mutex<T>>` puts the data inside the lock.
- Scoped threads (Rust 1.63) let threads borrow locals because they are joined before the scope ends.
- Rust does not prevent deadlocks, logic races or leaks.

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
