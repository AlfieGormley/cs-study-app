---
id: gc-rust-ownership
title: Rust ownership and borrowing
level: advanced
minutes: 15
summary: How Rust frees memory deterministically with no garbage collector and no use-after-free, through single ownership, moves, Drop, shared and mutable borrows, and lifetimes, plus the escape hatches (Rc, RefCell, unsafe) and what it costs to work this way.
---

Every approach so far has a price. Manual memory is fast but unsafe. Reference counting and tracing GC are safe, but they cost run time, memory headroom or pauses.

Rust takes a fourth route. Normal drops follow the language’s scope and ownership rules, with code emitted by the **compiler**, as C++'s RAII does, and the compiler also **proves** that no reference outlives what it points to. There is no garbage collector and no reference count unless you ask for one, and safe code is designed to avoid use-after-free, double free and data races through static restrictions and safe runtime abstractions, assuming sound compiler/library implementations.

The price is paid at compile time, in rules you have to learn.

## The three ownership rules

From *The Rust Programming Language*:

1. Each value has an **owner**: a variable, a field, or an element of a collection.
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

Assigning or passing a heap-owning value **moves** ownership. The old variable can't be used afterwards.

```rust
let s1 = String::from("hi");
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

For String a move transfers its pointer/length/capacity representation without cloning its buffer. Physical copies may be optimized away, and non-Copy values need not be on the stack or own heap memory.

Passing to a function moves too:

```rust
fn consume(s: String) {
    // s dropped at end of fn
}

let name = String::from("ann");
consume(name);
consume(name);  // E0382: moved value
```

Two escape routes:

- **`Copy` types** (integers, `f64`, `bool`, `char`, and tuples or arrays of them) permit implicit duplication, so the original remains usable. Copy describes semantics, not location: a Copy value can be stored in a heap object, and shared references to heap data are Copy too.
- **.clone()** invokes type-specific cloning. String clones its buffer, but Rc/Arc clones share an allocation; Clone is not a universal deep-copy guarantee.

> [!note] Compare C++
> std::move is a cast enabling move overloads; it does not itself move or modify the source. Standard-library moved-from objects generally remain valid with type-specific guarantees (a moved unique_ptr is empty). Rust rejects reading an uninitialized moved value, but permits reinitialization and valid uses of unmoved fields after partial moves.

## Drop order

Initialized local bindings are normally dropped at scope exit in reverse declaration order. Struct fields instead drop in declaration order:

```rust
struct Noisy(&'static str);
impl Drop for Noisy {
    fn drop(&mut self) {
        println!("drop {}", self.0);
    }
}

fn main() {
    let _a = Noisy("a");
    let _b = Noisy("b");
    {
        let _c = Noisy("c");
    }
    println!("end");
}
```

Output:

```
drop c
end
drop b
drop a
```

For a newly created temporary such as Guard::new(), let _ = ... does not retain it beyond the statement; let _guard = ... does. Applying a wildcard to an existing place does not necessarily move/drop it. Current rustc denies let _ = mutex.lock() by default via let_underscore_lock, because otherwise the temporary guard would immediately unlock.

Because drop is deterministic, `Drop` releases far more than memory: a `File` closes, a `MutexGuard` unlocks, a transaction wrapper may roll back according to that library’s documented Drop contract.

## Borrowing

Moving everything around would be painful, so Rust lets you **borrow**: take a reference without taking ownership.

- `&T` is a shared borrow: ordinary mutation is restricted, but interior-mutability types can provide controlled mutation, and you can have any number at once.
- `&mut T` is a **mutable** borrow: read-write, and it must be the **only** borrow while it's in use.

```rust
fn len(s: &String) -> usize { s.len() }

fn shout(s: &mut String) { s.push('!'); }

let mut s = String::from("hi");
let n = len(&s);   // borrow, s still owned
shout(&mut s);     // exclusive borrow
```

The rule is **aliasing XOR mutation**: at any moment you can have many readers or one writer, never both. That single rule rules out a surprising number of bugs.

### Iterator invalidation, caught at compile time

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);
println!("{first}");
```

```
error[E0502]: cannot borrow `v` as mutable
because it is also borrowed as immutable
```

This isn't pedantry. `push` may reallocate the vector's buffer to a bigger one and free the old one, leaving `first` pointing into freed memory. In C++ comparable code can compile and becomes a dangling-reference access if reallocation actually invalidates that reference. In Rust it can't be written in safe code.

### Non-lexical lifetimes

A borrow can end after its **last use**, before the block ends; control flow and destructor requirements also constrain its lifetime. Delete the `println!` above and the code compiles: `first` is never used after the `push`, so the borrows don't overlap. This refinement, *non-lexical lifetimes*, arrived in the 2018 edition and removed many spurious errors.

### Data races

The same rule prevents data races. A data race involves conflicting concurrent accesses, at least one a write, without the required synchronization; atomic/synchronized access is different. Exclusive `&mut` makes that impossible within safe code, and the `Send` and `Sync` traits extend the check across threads (the concurrency module covers these).

## Lifetimes

A reference must never outlive the value it points to. The compiler checks this with **lifetimes**: names for the region of code where a reference is valid.

```rust
let r;
{
    let x = 5;
    r = &x;
}               // x dropped here
println!("{r}");
```

```
error[E0597]: `x` does not live long enough
```

Most lifetimes are inferred. Annotations are needed when elision cannot describe the relationship, including some returned references and types containing references:

```rust
fn longest<'a>(a: &'a str, b: &'a str)
    -> &'a str {
    if a.len() > b.len() { a } else { b }
}
```

`'a` says: the result is valid only as long as **both** inputs are. Lifetimes are purely compile-time; they generate no code.

Returning a reference to a local is impossible to annotate correctly, so the compiler rejects it outright. In C that's the dangling-pointer bug from lesson 1; in Rust you return the owned value instead (`String`, not `&String`), which moves it to the caller.

## Shared ownership and interior mutability

Some data really does have several owners: a node in a graph, a cache shared across threads. Rust provides library types for this, and you opt in explicitly:

| Need | Type |
|---|---|
| single owner on the heap | `Box<T>` |
| shared, one thread | `Rc<T>` |
| shared, many threads | `Arc<T>` |
| mutate behind `&` | `RefCell<T>` |
| ...across threads | `Mutex<T>` |

`Rc` and `Arc` are reference counting (lesson 3), and so they can leak cycles; you break them with `Weak`. `RefCell` moves the borrow check to **run time**: calling `borrow_mut()` while another borrow is active **panics** instead of failing to compile. The common combinations are `Rc<RefCell<T>>` for shared mutable data in one thread and `Arc<Mutex<T>>` across threads.

> [!warning] Leaks are "safe"
> Rust's guarantee is memory **safety**, not freedom from leaks. An `Rc` cycle, `std::mem::forget` or `Box::leak` can all leak memory in safe code. Leaking can't cause undefined behaviour, so Rust allows it.

## unsafe

Some things can't be proven by the borrow checker: the internals of `Vec`, calling C, talking to hardware. Inside an `unsafe` block you can dereference raw pointers and call `unsafe` functions. The idea is to keep these blocks small and wrap them in safe APIs, so the audit surface is a few lines rather than the whole program. Safe libraries can encapsulate these unsafe operations.

## The costs

- **Learning curve.** Ownership restrictions can require redesign, especially for code accustomed to unrestricted sharing; no universal learning-time estimate is supplied.
- **Graph-shaped data.** Doubly linked lists, trees with parent pointers and general graphs fight single ownership. Common answers: store nodes in a `Vec` and use indices, use an arena, or use `Rc` plus `Weak`.
- **Compile times.** Generic instantiation, optimization and dependency structure affect build time. No universal Rust-versus-Go timing comparison is included without a specified benchmark.

What you get back: control over allocation and release without a mandatory tracing-GC pause, although destructors, cascades, allocators and locks can still take substantial time, and a whole class of security bugs (lesson 2) removed at compile time. This is why Android, Windows, the Linux kernel and major browsers have started writing new components in Rust.

## Key takeaways
- Ordinary ownership supplies normal drop points; it does not guarantee destruction after leaks, cycles or process termination.
- Assignment and argument passing move heap-owning values, and using a moved-from variable is a compile error, which rules out double frees.
- Borrows follow aliasing XOR mutation: many `&T` or one `&mut T`, which prevents iterator invalidation and data races.
- Lifetimes let the compiler prove no reference outlives its value, ruling out dangling pointers with no run-time cost.
- `Rc`, `Arc`, `RefCell` and `Mutex` opt in to shared ownership and run-time checks where static ownership doesn't fit, and `unsafe` isolates what can't be proven.
- Safe Rust rules out use-after-free and data races but not leaks.

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
