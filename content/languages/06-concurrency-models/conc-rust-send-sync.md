---
id: conc-rust-send-sync
title: Borrowing, Send and Sync
level: advanced
minutes: 3
sourceLesson: conc-structured-rust
summary: Ownership and Send/Sync jointly prevent unsynchronised conflicting access in sound safe Rust.
---

Structured scopes make task lifetimes visible. Rust addresses a separate problem: whether values and references can safely cross thread boundaries. This unit assumes sound standard-library and unsafe dependencies.

## Rust: data races as type errors

### Aliasing XOR mutation

Rust's ownership rules were designed for memory safety, but they also rule out data races. At any moment a value can have **either**:

- shared references `&T` (which prevent ordinary mutation but can allow synchronized interior mutability), **or**
- exactly one mutable reference `&mut T`.

A data race involves conflicting accesses to the same memory, at least one a write, without the required happens-before ordering; exact definitions and atomic-access exceptions depend on the language. It does not require the accesses to occur at the same physical instant. Borrowing plus Send/Sync rules prevent unsynchronized conflicting access in safe Rust, assuming sound unsafe implementations underneath:

```rust
// Both closures request exclusive use.
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
- `Mutex<T>` is `Sync` when `T` is `Send`, even if `T` is not `Sync`, because the lock ensures only one thread reaches the `T` at a time.
- A `MutexGuard` must be dropped (unlocking the mutex) on the thread that locked it, so it cannot be sent away.

`thread::spawn` requires its closure to be `Send + 'static`, so the compiler checks every captured value:

```rust
// Rc cannot cross thread boundaries.
let a = Rc::new(5);
let b = Rc::clone(&a);
thread::spawn(move || {
    println!("{b}");
});
// error[E0277]: `Rc<i32>` cannot be
// sent between threads safely
```

If this compiled, both threads could bump the non-atomic refcount at once, lose an update, and free the value while it was still in use. Swapping `Rc` for `Arc` fixes it at the cost of atomic increments.

## Key takeaways
- Ownership and Send/Sync jointly prevent unsynchronised conflicting access in sound safe Rust.
- Arc shares ownership; it does not make arbitrary contents safe to share.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/nomicon/send-and-sync.html)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/std/thread/fn.scope.html)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
