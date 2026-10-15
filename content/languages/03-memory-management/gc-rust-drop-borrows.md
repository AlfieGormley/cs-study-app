---
id: gc-rust-drop-borrows
title: "Drop order and exclusive borrowing"
level: advanced
minutes: 4
sourceLesson: gc-rust-ownership
summary: "Local bindings normally drop in reverse declaration order; fields drop in declaration order"
---

Owners provide normal release points; borrows let code use an owned value without transferring it. Review both the lifetime of the owner and the period during which a reference is actually used.

## Drop order

Initialized local bindings are normally dropped at scope exit in reverse declaration order. Struct fields instead drop in declaration order:

```rust
struct Noisy(&'static str);
impl Drop for Noisy {
    fn drop(&mut self) {
        // Observe the owner's normal drop
        // point.
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

Moving everything around would be painful, so Rust lets you take a **Rust borrow**: take a reference without taking ownership.

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
// Growth could invalidate a live reference.
v.push(4);
println!("{first}");
```

```
error[E0502]: cannot borrow `v` as mutable
because it is also borrowed as immutable
```

This isn't pedantry. `push` may reallocate the vector's heap buffer to a bigger one and free the old one, leaving `first` pointing into freed memory. In C++ comparable code can compile and becomes a dangling-reference access if reallocation actually invalidates that reference. In Rust it can't be written in safe code.



### Non-lexical lifetimes

A Rust borrow can end after its **last use**, before the block ends; control flow and destructor requirements also constrain its lifetime. Delete the `println!` above and the code compiles: `first` is never used after the `push`, so the borrows don't overlap. This refinement, *non-lexical lifetimes*, arrived in the 2018 edition and removed many spurious errors.

### Data races

The same rule prevents data races. A data race involves conflicting concurrent accesses, at least one a write, without the required synchronization; atomic/synchronized access is different. Exclusive `&mut` makes that impossible within safe code, and the `Send` and `Sync` traits extend the check across threads (the concurrency module covers these).

## Key takeaways
- Local bindings normally drop in reverse declaration order; fields drop in declaration order.
- Many shared borrows or one exclusive mutable borrow may be in use; interior-mutability abstractions supply controlled exceptions to ordinary shared mutation restrictions.
- Non-lexical lifetimes can end a borrow after its last use, preventing a live reference from overlapping a potentially reallocating push.

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
