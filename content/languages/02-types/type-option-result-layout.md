---
id: type-option-result-layout
title: Explicit absence, errors and layout
level: intermediate
minutes: 3
sourceLesson: type-adts-pattern-matching
summary: Option and Result expose absence and failure to the checker; extracting a value still needs handling.
---

Absence and failure are separate domain alternatives. Use the sum-type model from the previous lessons to make those alternatives visible to callers before considering their memory representation.

## Option and Result: no more null

Tony Hoare called the null reference his "billion-dollar mistake". The problem is that in Java, *every* reference type silently includes `null`, so the type `String` doesn't tell you whether a value can be missing.

An ADT makes absence explicit:

```haskell
data Maybe a = Nothing | Just a
```

The Rust option type (`Option<T>`) has two variants, `None` and `Some(T)`, and you can't use the `T` without matching (or calling a method that handles `None`). Errors work the same way with the Rust Result type, `Result<T, E>`, whose two variants are `Ok(T)` (success, holding a `T`) and `Err(E)` (failure, holding an error `E`):

```rust
fn parse_port(s: &str)
    -> Result<u16, String> {
    // Return Err when parsing fails.
    let n = s.parse::<u16>()
        .map_err(|e| e.to_string())?;
    // A parsed zero is still invalid here.
    if n == 0 {
        return Err("port 0".into());
    }
    Ok(n)
}
```

The `?` operator returns early on `Err`, giving exception-like brevity while keeping failure visible in the signature.

## Under the hood

Rust Box is the owning pointer used for indirection here. The layout guarantee below concerns the documented payload types, with sized referents and the specified allocator where applicable.

A common representation uses a tag and variant payload, but layout can be boxed or optimized. Rust guarantees that `Option<&T>` for sized `T` has the same size and alignment as the reference; the documented guarantee also includes `Option<Box<T>>` for sized `T` with the global allocator.

> [!note] Layout limit
> A universal byte count for `Option<u32>` is omitted because its layout is not guaranteed by the language. Measure a specified compiler and target if that size matters.

## Key takeaways
- Option and Result expose absence and failure to the checker; extracting a value still needs handling.
- Rust documents specific null-pointer optimisations, not one universal enum layout.

## Further reading
- [Rust standard library: Option representation](https://doc.rust-lang.org/std/option/index.html)
- [The Rust Book: Generic types](https://doc.rust-lang.org/book/ch10-01-syntax.html)
- [Java Language Specification: Types](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)
