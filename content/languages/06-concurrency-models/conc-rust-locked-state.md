---
id: conc-rust-locked-state
title: Locked state and borrowing with scoped threads
level: advanced
minutes: 3
sourceLesson: conc-structured-rust
summary: A Mutex stores the protected data and exposes shared access through its guard.
---

The previous unit defined Send, Sync and exclusive borrowing. Arc and Mutex combine those properties to express shared mutable state without relying on an unrelated lock variable.

### Shared mutable state, checked

To mutate shared data you combine `Arc` (shared ownership) with `Mutex` (exclusive access):

```rust
// The guard controls shared mutation.
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let c = Arc::new(Mutex::new(0));
    let mut hs = vec![];
    for _ in 0..4 {
        // Give the child another owner.
        let c = Arc::clone(&c);
        hs.push(thread::spawn(move || {
            for _ in 0..1000 {
                // Guard drops after this
                // step.
                *c.lock().unwrap() += 1;
            }
        }));
    }
    // Observe the total only after
    // completion.
    for h in hs { h.join().unwrap(); }
    println!("{}", *c.lock().unwrap());
}
// prints 4000
```

Compare the earlier shared-lock example. There the lock and the counter were separate variables, linked only by convention. Here the counter lives **inside** the `Mutex`, and concurrent shared access uses a lock guard; exclusive access to the mutex itself also permits safe `get_mut` or consuming `into_inner` without locking. Forgetting the lock is not a bug you can write. The lock is released when the guard is dropped, at the end of the statement here.

`lock()` returns a `Result` because of **poisoning**: if poisoning detects an unwinding panic while the guard is held, later lock calls return a poison error unless it is cleared; detection is advisory and has exceptions, warning that the data may be half-updated.

### Scoped threads: structure meets borrowing

`thread::spawn` needs `'static` because the new thread might outlive the current function, so it cannot borrow locals. **Scoped threads**, stable since Rust 1.63, are structured concurrency for threads: every thread spawned in the scope is joined before `scope` returns, so borrowing is safe.

```rust
// Scope joins before borrowed data ends.
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

Async Rust is less settled. `tokio::spawn` requires `'static + Send` futures, like `thread::spawn`. A sound "scoped spawn" for async is hard because a future can be dropped or leaked (`mem::forget` is safe Rust) without running to completion, so nothing guarantees the scope waits. Crates like `tokio::task::JoinSet` give partial structure: dropping the set requests task abortion but does not await cleanup; already-running `spawn_blocking` tasks cannot generally be aborted.

## A standalone atomic counter

An `AtomicI32` supports mutation through a shared reference. Its `fetch_add` performs an indivisible addition, so two scoped threads can each add one without needing two mutable borrows of an ordinary integer. For a counter whose value is only inspected after both threads have joined, `Ordering::Relaxed` is sufficient: the atomic operation preserves each increment, and joining supplies completion ordering. This does not make relaxed ordering a way to publish unrelated non-atomic payload data. A `Mutex<i32>` is another way to express the same counter invariant.

## Key takeaways
- A Mutex stores the protected data and exposes shared access through its guard.
- Mutex poisoning is advisory; successful locking does not establish application invariants.
- Scoped threads are joined before their borrowed local data can go away.
- An async task scope needs a sound cancellation and lifetime story, not just a collection of handles.

## Further reading
- [Rust atomic types and ordering](https://doc.rust-lang.org/std/sync/atomic/index.html)
- [Primary source: docs.python.org](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/nomicon/send-and-sync.html)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/std/thread/fn.scope.html)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
