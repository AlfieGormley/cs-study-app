---
id: gc-rust-shared-unsafe
title: "Shared ownership, interior mutability and unsafe"
level: advanced
minutes: 4
sourceLesson: gc-rust-ownership
summary: "Rc and Arc share ownership; RefCell checks borrow conflicts at run time, while Mutex supplies synchronised access for suitable types"
---

When a single owner plus temporary borrows does not fit the domain, Rust provides explicit shared-ownership and synchronisation types. Their extra run-time behaviour remains part of the design, and memory safety still does not mean freedom from leaks.

## Shared ownership and interior mutability

Some data really does have several owners: a node in a graph, a cache shared across threads. Rust provides library types for this, and you choose them explicitly:

| Need | Type |
|---|---|
| single owner on the heap | `Box<T>` |
| shared, one thread | `Rc<T>` |
| shared, many threads | `Arc<T>` |
| mutate behind `&` | `RefCell<T>` |
| ...across threads | `Mutex<T>` |

`Rc` and `Arc` are reference counting, and so they can leak cycles; you break them with `Weak`. `RefCell` moves the borrow check to **run time**: calling `borrow_mut()` while another borrow is active triggers a **run-time panic** instead of failing to compile. The common combinations are `Rc<RefCell<T>>` for shared mutable data in one thread and `Arc<Mutex<T>>` across threads.

> [!warning] Leaks are "safe"
> Rust's guarantee is memory **safety**, not freedom from leaks. An `Rc` cycle, `std::mem::forget` or `Box::leak` can all leak memory in safe code. A sound safe API cannot require a destructor to run for memory safety, because safe code can intentionally forget a value. Leaks can still exhaust resources or prevent progress.

## unsafe

Some things can't be proven by the borrow checker: the internals of `Vec`, calling C, talking to hardware. Inside an `unsafe` block you can dereference raw pointers and call `unsafe` functions. The idea is to keep these blocks small and wrap them in safe APIs, so the audit surface is a few lines rather than the whole program. Safe libraries can encapsulate these unsafe operations.

## The costs

- **Learning curve.** Ownership restrictions can require redesign, especially for code accustomed to unrestricted sharing; no universal learning-time estimate is supplied.
- **Graph-shaped data.** Doubly linked lists, trees with parent pointers and general graphs fight single ownership. Common answers: store nodes in a `Vec` and use indices, use an arena, or use `Rc` plus `Weak`.
- **Compile times.** Generic instantiation, optimization and dependency structure affect build time. No universal Rust-versus-Go timing comparison is included without a specified benchmark.

What you get back: control over allocation and release without a mandatory tracing-GC pause, although destructors, cascades, allocators and locks can still take substantial time, and static restrictions plus safe run-time abstractions that prevent many memory-validity and data-race failures, assuming sound compiler and library implementations. Concrete contexts include Android platform components, Linux kernel support, Firefox code and Windows-facing libraries. These are different scopes of adoption, not claims that the whole systems are written in Rust.

## Key takeaways
- Rc and Arc share ownership; RefCell checks borrow conflicts at run time, while Mutex supplies synchronised access for suitable types.
- Strong-reference cycles and intentional leaks can be memory-safe; use weak edges or another ownership design when reclamation matters.
- Unsafe operations require manually upheld contracts; keep the unsafe implementation small and expose a sound safe interface.

## Further reading
- [What is ownership? — The Rust Book](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
- [References and borrowing — The Rust Book](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
- [Validating references with lifetimes — The Rust Book](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html)
- [RefCell and interior mutability — The Rust Book](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html)
- [The Rustonomicon: ownership and lifetimes](https://doc.rust-lang.org/nomicon/ownership.html)
- [Primary verification source 2](https://doc.rust-lang.org/reference/destructors.html)
- [Primary verification source 3](https://doc.rust-lang.org/std/mem/fn.forget.html)
- [Primary verification source 4](https://doc.rust-lang.org/std/clone/trait.Clone.html)
- [Primary verification source 5](https://doc.rust-lang.org/std/vec/struct.Vec.html)
- [Primary verification source 6](https://doc.rust-lang.org/rustc/lints/listing/deny-by-default.html#let-underscore-lock)
- [Rust in Android platform code — Android security team](https://security.googleblog.com/2021/04/rust-in-android-platform.html)
- [Rust support — Linux kernel documentation](https://docs.kernel.org/rust/index.html)
- [Writing Rust code — Firefox source documentation](https://firefox-source-docs.mozilla.org/writing-rust-code/index.html)
- [Rust for Windows libraries — Microsoft](https://github.com/microsoft/windows-rs)
