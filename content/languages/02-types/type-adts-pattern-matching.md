---
id: type-adts-pattern-matching
title: Algebraic data types and pattern matching
level: intermediate
minutes: 14
summary: Building types from "and" and "or", counting their values, replacing null and error codes with Option and Result, and using exhaustive pattern matching in Haskell, Rust, TypeScript, Python and Java to make illegal states unrepresentable.
---

Most data is built from two ideas. An order has a customer **and** a list of items **and** a total. A payment is a card payment **or** a bank transfer **or** a voucher. Classes and structs handle "and" well. Many mainstream languages had no direct way to say "or", so programmers faked it with nullable fields, type codes and `instanceof` chains.

**Algebraic data types** (ADTs) give you both as first-class tools. Combined with **pattern matching**, which takes them apart safely, they are one of the most useful ideas to have spread from ML and Haskell into Rust, Swift, Kotlin, TypeScript, Python and Java.

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

It's called a product because of how the number of possible values combines. If `A` has `|A|` values and `B` has `|B|`, the pair `(A, B)` has `|A| × |B|`. A pair of `bool`s has 2 × 2 = 4 values.

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

Each alternative is a **constructor** (or variant) and may carry its own data. The counts add: `|A + B| = |A| + |B|`. That is the "algebra": types built from sums and products.

| Type | Values |
|---|---|
| `()` / unit | 1 |
| `bool` | 2 |
| `(bool, bool)` | 2 × 2 = 4 |
| `Option<bool>` | 1 + 2 = 3 |
| `Result<bool, ()>` | 2 + 1 = 3 |
| An empty type, such as Rust `!` | 0 |

These counts concern fully defined finite values, excluding nontermination and partial values. Names like Java `Void` do not necessarily denote an uninhabited type. Counting is practical, not academic. If your domain has 3 valid states and your type has 4, one value of the type is a bug waiting to happen.

## Pattern matching

A **pattern match** checks which alternative a value is and binds its fields in one step:

```haskell
area :: Shape -> Double
area (Circle r) = pi * r * r
area (Rect w h) = w * h
```

```rust
fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle { r } =>
            std::f64::consts::PI * r * r,
        Shape::Rect { w, h } => w * h,
    }
}
```

Patterns nest, so you can match deep structure, and they can carry **guards**:

```rust
enum Cmd { Quit, Buy(u32) }

match (cmd, logged_in) {
    (Cmd::Quit, _) => quit(),
    (Cmd::Buy(n), true) if n > 0 => buy(n),
    (Cmd::Buy(_), true) => bad_qty(),
    (_, false) => login(),
}
```

Arms are tried **top to bottom**, and the first match wins. Order matters: put specific cases before general ones.

### Exhaustiveness

The big win is that the compiler knows every alternative, so it can check that you handled them all:

- **Rust**: a non-exhaustive `match` is a hard error (E0004), and it names the missing pattern.
- **Haskell**: GHC warns about incomplete patterns (with `-Wall`); at run time an unmatched value throws.
- **Java 21**: a `switch` over a `sealed` type must cover every permitted subtype.
- **TypeScript, Python**: possible with a `never`-typed trick, shown below.

Add a `Triangle` variant, and an exhaustiveness check can flag matches lacking both that case and a catch-all. In a class hierarchy with `instanceof` chains, the compiler can't tell you.

## Recursive types: trees and expressions

Sum types can refer to themselves. An arithmetic expression is a number, or an operation on smaller expressions:

```haskell
data Expr
  = Num Int
  | Add Expr Expr
  | Mul Expr Expr
  | Neg Expr

eval :: Expr -> Int
eval (Num n)   = n
eval (Add a b) = eval a + eval b
eval (Mul a b) = eval a * eval b
eval (Neg e)   = negate (eval e)
```

`eval (Add (Num 2) (Mul (Num 3) (Num 4)))` is 2 + 12 = 14. Compilers use exactly this shape for their syntax trees, which is why ML-family languages are popular for writing compilers. In Rust a recursive variant needs indirection (`Add(Box<Expr>, Box<Expr>)`), otherwise the type would have infinite size.

## Option and Result: no more null

Tony Hoare called the null reference his "billion-dollar mistake". The problem is that in Java, *every* reference type silently includes `null`, so the type `String` doesn't tell you whether a value can be missing.

An ADT makes absence explicit:

```haskell
data Maybe a = Nothing | Just a
```

Rust's `Option<T>` is `None | Some(T)`, and you can't use the `T` without matching (or calling a method that handles `None`). Errors work the same way with `Result<T, E>` = `Ok(T) | Err(E)`:

```rust
fn parse_port(s: &str)
    -> Result<u16, String> {
    let n = s.parse::<u16>()
        .map_err(|e| e.to_string())?;
    if n == 0 {
        return Err("port 0".into());
    }
    Ok(n)
}
```

The `?` operator returns early on `Err`, giving exception-like brevity while keeping failure visible in the signature.

## Sum types in other languages

### TypeScript: discriminated unions

A union of object types that share a literal **tag** field:

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r ** 2;
    case "rect":
      return s.w * s.h;
    default: {
      const gone: never = s;
      return gone;
    }
  }
}
```

Checking `s.kind` **narrows** `s` in each branch. In `default`, every case has been removed, so `s` has type `never`. Add a `"triangle"` member and the assignment to `never` fails to compile: a hand-made exhaustiveness check.

### Python: dataclasses and `match`

Python 3.10 added structural pattern matching:

```python
import math
from dataclasses import dataclass
from typing import assert_never

@dataclass
class Circle:
    r: float

@dataclass
class Rect:
    w: float
    h: float

Shape = Circle | Rect

def area(s: Shape) -> float:
    match s:
        case Circle(r=r):
            return math.pi * r * r
        case Rect(w=w, h=h):
            return w * h
        case _:
            assert_never(s)
```

Python itself does not statically check exhaustiveness. Without a matching arm execution continues after the match; the shown catch-all instead calls `assert_never`, which raises at runtime. But mypy and Pyright narrow `s` in each case, and `typing.assert_never` (3.11+) makes a missing case a type error.

### Java: sealed interfaces and records

Java 17 added `sealed` types and Java 21 finalised pattern matching for `switch` and record patterns:

```java
sealed interface Shape
    permits Circle, Rect {}
record Circle(double r)
    implements Shape {}
record Rect(double w, double h)
    implements Shape {}

static double area(Shape s) {
  return switch (s) {
    case Circle c ->
        Math.PI * c.r() * c.r();
    case Rect(double w, double h) ->
        w * h;
  };
}
```

No `default` is needed, because the compiler knows the permitted implementations. A null selector still throws `NullPointerException` unless a `case null` handles it.

## Make illegal states unrepresentable

Yaron Minsky's slogan from Jane Street sums up the design use. Compare two models of a network connection:

```ts
// 2 × 2 × 2 = 8 shapes (each optional
// field present or absent), most nonsense
type Conn = {
  connected: boolean;
  sessionId?: string;
  error?: string;
};

// three explicit state alternatives
type Conn2 =
  | { state: "idle" }
  | { state: "live"; sessionId: string }
  | { state: "failed"; error: string };
```

With the first, nothing stops `connected: false` with a `sessionId`, and every reader has to guess. With the second, narrowing to the live alternative guarantees a session id under the checked type. TypeScript structural typing can still admit additional properties; this is not runtime validation or a guarantee of exact object shape. Related advice: **parse, don't validate**. Turn raw input into a precise type once at the boundary, and the rest of the code can rely on it.

## The expression problem

ADTs and classes make opposite things easy. Philip Wadler named this the **expression problem** (1998):

| | Add a new operation | Add a new variant |
|---|---|---|
| ADT + match | Easy: one new function | Edit every match |
| Classes | Edit every class | Easy: one new class |

With an `Expr` ADT, adding `prettyPrint` is one function; adding `Div` touches `eval`, `prettyPrint` and every other match (and the compiler lists them). With an `Expr` class hierarchy it's the reverse. Choose ADTs when the set of cases is stable and operations grow, as in compilers and protocol messages.

## Under the hood

A common representation uses a tag and variant payload, but layout can be boxed or optimized. Rust guarantees that `Option<&T>` for sized `T` has the same size and alignment as the reference; the documented guarantee also includes `Option<Box<T>>` for sized `T` with the global allocator.

> [!note] Layout limit
> A universal byte count for `Option<u32>` is omitted because its layout is not guaranteed by the language. Measure a specified compiler and target if that size matters.

## Pitfalls

- **Wildcard catch-alls.** A `_ =>` arm silences exhaustiveness checking, so a new variant is silently handled by the default. Prefer listing cases.
- **Order of arms.** A general pattern above a specific one makes the specific one unreachable. Rust and GHC warn about this.
- **Boolean blindness.** `process(true, false)` says nothing. An enum like `Mode::DryRun` makes intent explicit.
- **Unwrapping everywhere.** `.unwrap()` and Haskell's `fromJust` turn `None` back into a crash, undoing the point of `Option`.
- **Python's `match` isn't `switch`.** A bare name in a `case` binds a new variable rather than comparing against an existing one. `case RED:` matches anything; use `case Color.RED:`.

## Key takeaways
- Product types combine values with "and" (counts multiply); sum types choose one alternative with "or" (counts add).
- Pattern matching tests the variant and binds its fields at once; nested patterns and guards handle complex cases.
- Exhaustiveness checking makes adding a variant safe: the checker can flag uncovered cases; catch-all arms can hide newly added variants.
- `Option`/`Maybe` and `Result`/`Either` make absence and failure visible in types instead of hiding them in null and exceptions.
- TypeScript (discriminated unions plus `never`), Python (`match` plus `assert_never`) and Java 21 (sealed types plus `switch`) all now support the pattern.
- Model the domain so that invalid states can't be constructed, and parse input into precise types at the boundary.

## Further reading
- [Algebraic data type — Wikipedia](https://en.wikipedia.org/wiki/Algebraic_data_type)
- [Enums and pattern matching — The Rust Programming Language](https://doc.rust-lang.org/book/ch06-00-enums.html)
- [PEP 636: Structural pattern matching tutorial](https://peps.python.org/pep-0636/)
- [JEP 441: Pattern matching for switch](https://openjdk.org/jeps/441)
- [Narrowing and discriminated unions — TypeScript handbook](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [Effective ML revisited — Jane Street blog](https://blog.janestreet.com/effective-ml-revisited/)
- [Parse, don't validate — Alexis King](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- [Expression problem — Wikipedia](https://en.wikipedia.org/wiki/Expression_problem)
- [Primary verification source 1](https://doc.rust-lang.org/std/option/index.html)
- [Primary verification source 2](https://docs.python.org/3/library/typing.html)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/21/language/java-language-changes-release.html)
