---
id: gc-rust-moves-owners
title: "Rust owners, moves and copies"
level: advanced
minutes: 4
sourceLesson: gc-rust-ownership
summary: "A Rust move transfers a non-Copy value and leaves the moved place uninitialised until valid reinitialisation"
---

Every approach so far has a price. Manual allocation offers explicit control but relies on correct lifetime management. Reference counting and tracing can automate reclamation within sound implementations, while adding run-time work, metadata, headroom or pauses. None is universally fastest.

Rust takes a fourth route. Normal drops follow the language’s scope and ownership rules, with code emitted by the **compiler**, as C++'s RAII does, and the compiler also **proves** that no reference outlives what it points to. Ordinary Rust ownership requires neither a tracing garbage collector nor reference counting; library types can add counting, and safe code is designed to avoid use-after-free, double free and data races through static restrictions and safe runtime abstractions, assuming sound compiler/library implementations.

The price is paid at compile time, in rules you have to learn.

## The three ownership rules

From *The Rust Programming Language*:

1. Each value has a **memory owner**: a variable, a field, or an element of a collection.
2. There can be only **one owner at a time**.
3. When the owner goes **out of scope**, the value is **dropped** (its memory and resources are released).

```rust
fn main() {
    let s = String::from("hello");
    // s owns a heap buffer
}   // s goes out of scope: buffer freed
```

For this example the compiler emits destruction at scope exit. Rust does not guarantee every destructor runs: intentional leaks, cycles, abort and process exit are exceptions.

## Moves

Assigning or passing an owned non-Copy value by value **moves** it. A borrow does not, and the moved place can be used again after valid reinitialisation; partial moves have more precise field rules.

```rust
let s1 = String::from("hi");
// Transfer the value without cloning text.
let s2 = s1;          // ownership moves
println!("{s1}");     // compile error
```

```
error[E0382]: borrow of moved value: `s1`
```

Why forbid it? Both `s1` and `s2` would point at the same heap buffer, and both would free it at the end of scope: a **double free**. Rust's answer is that after the move, only `s2` owns it, so exactly one free happens.

```
 after `let s2 = s1;`

 s1 (invalid)      s2
 +---------+      +---------+     heap
 | ptr     |      | ptr  ---+--> "hi"
 | len, cap|      | len, cap|
 +---------+      +---------+
```

For String a move transfers its pointer/length/capacity representation without cloning its heap buffer. Physical copies may be optimized away, and non-Copy values need not be on the stack or own heap memory.

Passing to a function moves too:

```rust
fn consume(s: String) {
    // s dropped at end of fn
}

let name = String::from("ann");
consume(name);
// The second call tries to reuse moved
// data.
consume(name);  // E0382: moved value
```

Two escape routes:

- **`Copy` types** (integers, `f64`, `bool`, `char`, and tuples or arrays of them) permit implicit duplication, so the original remains usable. Copy describes semantics, not location: a Copy value can be stored in a heap object, and shared references to heap data are Copy too.
- **.clone()** invokes type-specific cloning. String clones its heap buffer, but Rc/Arc clones share an allocation; Clone is not a universal deep-copy guarantee.

> [!note] Compare C++
> std::move is a cast enabling move overloads; it does not itself move or modify the source. Standard-library moved-from objects generally remain valid with type-specific guarantees (a moved unique_ptr is empty). Rust rejects reading an uninitialized moved value, but permits reinitialization and valid uses of unmoved fields after partial moves.

## Key takeaways
- A Rust move transfers a non-Copy value and leaves the moved place uninitialised until valid reinitialisation.
- Copy permits implicit duplication, while Clone runs type-specific code and need not make a deep copy.
- Normal ownership-driven drops differ from guaranteed destruction in every execution; safe intentional leaks and termination remain possible.

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
