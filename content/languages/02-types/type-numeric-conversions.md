---
id: type-numeric-conversions
title: Numeric conversions and type safety
level: basic
minutes: 3
sourceLesson: type-static-dynamic
summary: Rust requires an explicit integer widening conversion; Java permits selected widening and string conversions.
---

Python and JavaScript illustrated different mixed-type operations in the previous unit. Static languages also differ: inspect their numeric conversion rules and safety guarantees separately.

## Numeric conversions

C is statically typed but weak in an important sense. It converts freely between numeric types (`int x = 3.9;` silently truncates to 3), and pointer casts can bypass useful static checks. A cast alone need not be erroneous, but invalid alignment or accessing an object through an incompatible type can cause undefined behaviour.

Rust is at the strict end even for numbers. It will not widen an `i32` to an `i64` without being asked:

```rust
let a: i32 = 5;
let b: i64 = a;        // error: mismatched
let c: i64 = a.into(); // ok, explicit
```

Java, by contrast, widens `int` to `long` silently, and `"a" + 1` is `"a1"` because `+` with a String converts the other side.



## The two axes together

| | Strong-ish | Weak-ish |
|---|---|---|
| **Static** | Rust, Haskell, Java | C, C++ |
| **Dynamic** | Python, Ruby | JavaScript, PHP |

Treat this as a rough map, not a ranking. Every language makes some coercions and forbids others.

A more precise discussion names the actual **type safety** property and its assumptions: the guarantee that a program which passes the checks can never perform an operation on a value of the wrong type in a way that corrupts memory or gets "stuck". Robin Milner summarised it in 1978 as **"well-typed programs cannot go wrong"**. A checked Java cast can raise `ClassCastException`, and a Python operation can raise `TypeError`, rather than reinterpreting an object as arbitrary memory. These runtime protections differ from a proof that every statically accepted source program avoids unexpected type mismatches. C permits undefined behaviour in cases such as invalid typed memory access.



## Key takeaways
- Rust requires an explicit integer widening conversion; Java permits selected widening and string conversions.
- Static checking and memory safety are separate properties.

## Further reading
- [Java Language Specification: Conversions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html)
- [The Rust Book: Generic types](https://doc.rust-lang.org/book/ch10-01-syntax.html)
- [Luca Cardelli: Type systems](https://lucacardelli.name/Papers/TypeSystems.pdf)
- [C11 draft standard](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
