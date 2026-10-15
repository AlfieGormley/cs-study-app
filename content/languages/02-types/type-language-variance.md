---
id: type-language-variance
title: Variance across language designs
level: intermediate
minutes: 4
sourceLesson: type-subtyping-variance
summary: Kotlin and C# support declaration-site variance; Python checkers infer or declare it.
---

Variance rules become practical when an API declares which values it produces and consumes. The examples retain the earlier Animal supertype and Dog subtype; they illustrate each language’s static rules rather than one cross-language runtime model.

## Declaration-site variance

Writing wildcards at every use is noisy. Kotlin, C# and Scala let the *type's author* declare variance once:

```kotlin
interface Source<out T> {
    fun next(): T      // T only out
}
interface Sink<in T> {
    fun put(x: T)      // T only in
}
```

The compiler checks the declaration: using an `out T` as a method parameter is an error. Kotlin's read-only `List<out E>` is covariant; `MutableList<E>` is invariant. C# marks `IEnumerable<out T>` and `Action<in T>` the same way, though only on interfaces and delegate types (C#'s named function types). TypeScript 4.7 added optional `in`/`out` annotations on type parameters, mainly to make variance explicit and checking faster.

## Python: invariant lists, covariant sequences

Python's type checkers follow the same rules. `list` is mutable, so it's invariant; `Sequence` is read-only, so it's covariant:

```python
from collections.abc import Sequence

def feed(xs: list[Animal]) -> None: ...
def show(xs: Sequence[Animal]) -> None: ...

dogs: list[Dog] = [Dog()]
feed(dogs)  # mypy error: invariant
show(dogs)  # ok: Sequence is covariant
```

`Callable[[Animal], None]` is usable where `Callable[[Dog], None]` is expected (contravariant parameters). For your own generics, older code declares `TypeVar("T_co", covariant=True)`; the Python 3.12 syntax `class Box[T]:` lets the checker **infer** variance from how `T` is used.

## Rust: lifetimes and higher-ranked types

Rust has no class inheritance; traits use bounds rather than a Dog/Animal class-subtyping hierarchy. Its subtyping includes lifetime relationships and higher-ranked function/trait-object types. For references, a longer lifetime can be shortened: the longer reference can satisfy a shorter required lifetime, provided the referent type and other typing conditions also fit. A reference that lives longer can be used where a shorter one is needed. So `&'static str` can go wherever `&'a str` is expected.

Variance still matters, and the compiler infers it from each type's fields:

| Type | Variance in `T` |
|---|---|
| `&'a T`, `Box<T>`, `Vec<T>` | Covariant |
| `&'a mut T` | Invariant |
| `Cell<T>` | Invariant |
| `fn(T) -> U` | Contra in `T`, co in `U` |

`&mut T` is invariant for exactly the mutable-list reason: if `&mut &'static str` could be treated as `&mut &'a str`, you could write a short-lived string through it and later read it back as `'static`, a dangling reference.

## Variance trade-offs and runtime checks

| Language | Hole | Outcome |
|---|---|---|
| Java, C# | Covariant arrays | Run-time store check |
| TypeScript | Covariant arrays | Silent, crashes later |
| TypeScript | Method params bivariant | Silent |
| Eiffel | Covariant method params | Catcall/type-validity concerns |

TypeScript's `strictFunctionTypes` (part of `strict`) applies to ordinary function types and function-typed properties. Parameters of methods and constructors declared with method syntax stay bivariant, so DOM-style event handler interfaces keep working:

```ts
// method syntax: bivariant
interface A { m(x: Dog): void }

// property syntax: contravariant
interface B { m: (x: Dog) => void }
```

## Pitfalls

- **Expecting `List<Dog>` to be a `List<Animal>`.** In Java, Python's `list` and Kotlin's `MutableList` it isn't. Accept `List<? extends Animal>`, `Sequence[Animal]` or `List<Animal>` (read-only) instead.
- **Trusting TypeScript arrays.** Passing `Dog[]` as `Animal[]` to a function that pushes into it compiles and corrupts the caller's array. Prefer `readonly Animal[]` parameters.
- **Overriding with a narrower parameter.** A subclass method that only accepts `Dog` where the parent accepted `Animal` breaks substitution. Java treats it as an overload, not an override.
- **Confusing structural fits with intent.** In TypeScript, two unrelated interfaces with the same shape are interchangeable. Use branded types when that matters.

## Key takeaways
- Kotlin and C# support declaration-site variance; Python checkers infer or declare it.
- Rust subtyping involves lifetimes and higher-ranked types; exclusive mutation explains key invariance rules.
- TypeScript method parameters remain bivariant under strictFunctionTypes.

## Further reading
- [Kotlin: Generics and variance](https://kotlinlang.org/docs/generics.html)
- [Python spec](https://typing.python.org/en/latest/spec/generics.html)
- [Rustonomicon: Subtyping and variance](https://doc.rust-lang.org/nomicon/subtyping.html)
- [Rust Reference: Subtyping](https://doc.rust-lang.org/reference/subtyping.html)
- [TypeScript 2.6: Strict function types](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-6.html)
- [TypeScript 4.7: Variance annotations](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-7.html)
