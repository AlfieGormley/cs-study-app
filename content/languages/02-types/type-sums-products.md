---
id: type-sums-products
title: Building types from sums and products
level: intermediate
minutes: 4
sourceLesson: type-adts-pattern-matching
summary: Products combine all fields and multiply finite value counts; tagged alternatives add them.
---

Most data is built from two ideas. An order has a customer **and** a list of items **and** a total. A payment is a card payment **or** a bank transfer **or** a voucher. Classes and structs handle "and" well. Many mainstream languages had no direct way to say "or", so programmers faked it with nullable fields, type codes and `instanceof` chains.

**Algebraic data types** (ADTs) give you both as built-in tools. Combined with **pattern matching**, which takes them apart safely, they are one of the most useful ideas to have spread from ML and Haskell into Rust, Swift, Kotlin, TypeScript, Python and Java.

## Product types: "and"

A **product type** holds several values at once: a tuple, struct or record.

```rust
struct Point { x: i32, y: i32 }
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int
```

It's called a product because of how the number of possible values combines. A pair holds one value from each part, and every combination is allowed, so the counts multiply:

```formula
|A × B| = |A| × |B|
|bool × bool| = 2 × 2 = 4
where
A, B: any two types
A × B: the product type: a pair (tuple) holding one A and one B, written (A, B) in code
|A|: the cardinality of A: how many distinct values the type A has
bool: the Boolean type, with the 2 values true and false
×: between types, "a pair of"; between numbers, ordinary multiplication
In words: a pair has one value for every combination of its parts, so a pair of bools has 4 values: (false, false), (false, true), (true, false) and (true, true).
```

## Sum types: "or"

A **sum type** (also called a tagged union, variant or discriminated union) holds exactly **one** of several alternatives, and records which one.

```haskell
data Shape
  = Circle Double
  | Rect Double Double
```

```rust
enum Shape {
    Circle { r: f64 },
    Rect { w: f64, h: f64 },
}
```

Each alternative is a **data constructor** (or variant) and may carry its own data. A value is one alternative *or* another, never both, so the counts add:

```formula
|A + B| = |A| + |B|
|Option<bool>| = 1 + 2 = 3
where
A, B: any two types
A + B: the sum type: either an A or a B, tagged with which one it is
|A|: the cardinality of A: how many distinct values A has
Option<bool>: Rust's optional bool: None (1 value) or Some holding a bool (2 values)
bool: the Boolean type, with the 2 values true and false
+: between types, "one or the other"; between numbers, ordinary addition
In words: a sum type has the values of its first alternative plus the values of its second, so an optional bool has 3: None, Some(true) and Some(false).
```

That is the "algebra": types built from sums and products.

| Type | Values |
|---|---|
| `()` / unit | 1 |
| `bool` | 2 |
| `(bool, bool)` | 2 × 2 = 4 |
| `Option<bool>` | 1 + 2 = 3 |
| `Result<bool, ()>` | 2 + 1 = 3 |
| An empty type, such as Rust `!` | 0 |

These counts concern fully defined finite values, excluding nontermination and partial values. Names like Java `Void` do not necessarily denote an uninhabited type. Counting is practical, not academic. If your domain has 3 valid states and your type has 4, one value of the type is a bug waiting to happen.

## Key takeaways
- Products combine all fields and multiply finite value counts; tagged alternatives add them.
- The counts concern defined finite values, not nontermination or arbitrary representation bytes.

## Further reading
- [Haskell 2010: Declarations and types](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
- [Rust standard library: Option representation](https://doc.rust-lang.org/std/option/index.html)
- [The Rust Book: Generic types](https://doc.rust-lang.org/book/ch10-01-syntax.html)
