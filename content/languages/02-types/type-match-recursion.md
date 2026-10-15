---
id: type-match-recursion
title: Matching variants and recursive syntax
level: intermediate
minutes: 3
sourceLesson: type-adts-pattern-matching
summary: Match arms run in order, and guards further restrict an arm.
---

The preceding lesson introduced Shape as either Circle with a radius or Rect with width and height. The following pattern examples use those constructors; numeric lengths share one unit, and returned areas use its square.

## Pattern matching

A **pattern match** checks which alternative a value is and binds its fields in one step:

```haskell
area :: Shape -> Double
area (Circle r) = pi * r * r
area (Rect w h) = w * h
```

```rust
fn area(s: &Shape) -> f64 {
    // Bind fields of the selected variant.
    match s {
        Shape::Circle { r } =>
            std::f64::consts::PI * r * r,
        Shape::Rect { w, h } => w * h,
    }
}
```

Patterns nest, so you can match deep structure, and they can carry **pattern guards** (an extra `if` condition on an arm):

```rust
enum Cmd { Quit, Buy(u32) }

match (cmd, logged_in) {
    (Cmd::Quit, _) => quit(),
    // A guard further restricts a match.
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

Add a `Triangle` variant, and an exhaustiveness check can flag matches lacking both that case and a catch-all arm. An ordinary open class hierarchy tested only with `instanceof` chains does not provide that same closed-set exhaustiveness check.

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
-- Evaluate both child expressions first.
eval (Add a b) = eval a + eval b
eval (Mul a b) = eval a * eval b
-- Negation applies to the entire subtree.
eval (Neg e)   = negate (eval e)
```

`eval (Add (Num 2) (Mul (Num 3) (Num 4)))` is 2 + 12 = 14. Compilers use exactly this shape for their syntax trees, which is why ML-family languages are popular for writing compilers. In Rust a recursive variant needs indirection (`Add(Box<Expr>, Box<Expr>)`), otherwise the type would have infinite size.

## Key takeaways
- Match arms run in order, and guards further restrict an arm.
- Exhaustiveness can expose a new unhandled variant; a catch-all can conceal it.
- Recursive expression trees evaluate by recursively visiting their constructors.

## Further reading
- [The Rust Book: Pattern syntax](https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html)
- [Haskell 2010: Declarations and types](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
- [GHC warning flags](https://downloads.haskell.org/ghc/latest/docs/users_guide/using-warnings.html)
- [JEP 441: Pattern matching for switch](https://openjdk.org/jeps/441)
