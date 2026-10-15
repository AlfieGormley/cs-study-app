---
id: gc-rust-reference-lifetimes
title: "Rust reference lifetimes"
level: advanced
minutes: 3
sourceLesson: gc-rust-ownership
summary: "A lifetime annotation describes a relationship between references; it neither extends storage lifetime nor adds a run-time keep-alive mechanism"
---

Ownership identifies the value responsible for release. Lifetimes relate how long references can remain valid, especially when a function chooses between references supplied by its caller.

## Lifetimes

A reference must never outlive the value it points to. The compiler checks this with **Rust lifetimes**: names for the region of code where a reference is valid.

```rust
let r;
{
    let x = 5;
    // This borrow cannot extend x's
    // storage.
    r = &x;
}               // x dropped here
println!("{r}");
```

```
error[E0597]: `x` does not live long enough
```

Most lifetimes are inferred. Lifetime annotations are needed when lifetime elision cannot describe the relationship, including some returned references and types containing references:

```rust
fn longest<'a>(a: &'a str, b: &'a str)
    -> &'a str {
    // Return a borrow of one input, no
    // copy.
    if a.len() > b.len() { a } else { b }
}
```

The shared lifetime parameter relates the returned reference to both input borrows. At a call site it constrains how long the result may be used; it does not extend either input's storage lifetime. Lifetime checking is a compile-time mechanism, not a run-time reference-count operation.

Returning a reference to an ordinary automatic local that is destroyed at return cannot be made valid by an annotation, so safe Rust rejects it. References to static storage or deliberately leaked allocations are different cases. In C that's the dangling-pointer bug in Automatic lifetimes and Python references; in Rust you return the owned value instead (`String`, not `&String`), which moves it to the caller.

## Read a lifetime relationship

The annotation on longest does not keep either input alive and does not select an exact duration at run time. At a call site the compiler must find a suitable overlapping validity region for the input borrows and returned borrow. An input string may live much longer than that common region.

For example, if one input is owned in an inner block and the other in an outer block, a result that might refer to the inner one cannot be used after the inner owner is dropped. Keeping the longer-lived input around does not rescue a possibly dangling result. Returning an owned String instead changes the contract by transferring a value rather than borrowing either input.

A common lifetime-elision rule relates a returned reference to the only input-reference lifetime. With two independent input-reference lifetimes, a free function such as longest needs an explicit relationship; method receiver rules are a separate case.

Lifetime elision supplies common relationships automatically; it does not remove the underlying validity checks. An annotation documents and constrains relationships the compiler must verify. It cannot make a local variable survive its destruction or permit a reference to expired storage.

## Key takeaways
- A lifetime annotation describes a relationship between references; it neither extends storage lifetime nor adds a run-time keep-alive mechanism.
- longest must return a reference usable only within the validity region supported by both input borrows.
- Returning an owned value is different from returning a reference to an expired local.

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
