---
id: type-generics
title: Generics and parametric polymorphism
level: intermediate
minutes: 13
summary: Writing code once for every type without losing type information, bounded generics, what parametricity guarantees, and how Java, Rust, C#, Haskell, TypeScript and Python actually implement generics.
---

You want a function that returns the first element of a list. Lists of ints, lists of strings, lists of users: the logic is identical. In a statically typed language without generics you have two bad options.

1. Write it once per type: `firstInt`, `firstString`, `firstUser`. Duplicated code.
2. Write it once for "anything", using `Object` or `void*`, and cast the result back. The type checker loses track, and a wrong cast fails at run time (or, in C, silently).

Java before version 5 (2004) used non-generic collections. This modern raw-list example illustrates that API style; the autoboxing of `42` itself requires Java 5 or later:

```java
List names = new ArrayList();
names.add("Ada");
names.add(42);  // nothing stops this
String s = (String) names.get(1);
// ClassCastException at run time
```

**Generics** fix this. A type gets a **type parameter**, a placeholder filled in at each use, and the checker tracks it:

```java
List<String> names = new ArrayList<>();
names.add(42);  // compile error
String s = names.get(0); // no cast
```

## Parametric polymorphism

A function that works uniformly for every type is **parametrically polymorphic**. "Uniformly" is the important word: it runs the same code whatever the type, never inspecting it.

```haskell
first :: [a] -> Maybe a
first []      = Nothing
first (x : _) = Just x
```

```ts
function first<T>(xs: T[]): T | undefined {
  return xs[0];
}
const n = first([1, 2]);
// n: number | undefined
```

```python
def first[T](xs: list[T]) -> T:
    return xs[0]   # Python 3.12+ syntax
```

On an empty list these examples differ: Haskell returns `Nothing`, TypeScript returns `undefined`, and Python raises `IndexError`. The type variable (`a`, `T`) links the input to the output. Calling `first` on a list of numbers gives a number back, and the checker knows it.

This is one of three kinds of polymorphism:

| Kind | Idea | Example |
|---|---|---|
| Parametric | Same code for all types | `first<T>` |
| Ad hoc | Different code per type | Overloading, type classes |
| Subtype | Use a subclass where a superclass is expected | `Animal a = new Dog()` |

## Bounded generics

Fully parametric code can't *do* much with a `T`: it can store it, return it and pass it along, but not compare or print it. To use operations, you **bound** the type parameter: "any `T`, as long as it supports X".

```java
static <T extends Comparable<T>>
T max(List<T> xs) { ... }
```

```rust
fn largest<T: PartialOrd + Copy>(
    xs: &[T],
) -> T {
    let mut best = xs[0];
    for &x in xs {
        if x > best { best = x; }
    }
    best
}
```

```haskell
maximum' :: Ord a => [a] -> a
```

```ts
function longest<
  T extends { length: number }
>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
longest("abc", "de");  // ok
longest(10, 20);       // error: number
                       // has no 'length'
```

In Python, a bound can be a `Protocol`, which checks structurally:

```python
from typing import Protocol, Self

class Ordered(Protocol):
    def __lt__(self, other: Self) -> bool:
        ...

def biggest[T: Ordered](xs: list[T]) -> T:
    best = xs[0]
    for x in xs[1:]:
        if best < x:
            best = x
    return best
```

These maximum examples require nonempty inputs and meaningful ordering; `PartialOrd` also admits incomparable values such as NaN, so the Rust loop is not a universal mathematical maximum. mypy accepts `biggest([3, 9, 4])` (result `int`) and rejects `biggest([object()])`, because `object` has no usable `__lt__`.

## Parametricity: types as theorems

Under total parametric semantics (excluding nontermination, exceptions, `seq` and unsafe inspection), because a parametric function cannot inspect its `T`, its type alone tells you a surprising amount about what it does. Philip Wadler called this **theorems for free** (1989).

- `f :: a -> a`. The only thing `f` can do with an unknown `a` is return it. So `f` must be the identity (or never return).
- `g :: [a] -> [a]`. `g` cannot invent new `a` values or look at them. It can only drop, duplicate and reorder elements based on the list's **shape**. For finite lists, `reverse` and `take 3` fit; `cycle` is a partial, potentially infinite example outside this total finite-list statement; `sort` does not (it needs `Ord a`).
- A consequence: for any such `g` and any function `h`, `map h (g xs) == g (map h xs)`.

This only holds if the language really is uniform. Java breaks it: a generic method can call `instanceof`, `getClass()` or `hashCode()` on a `T`. TypeScript can use `typeof`; Python can use `type` or `isinstance`. Haskell supports useful parametric reasoning subject to those caveats. Rust generics also permit observations such as `size_of::<T>()`, so merely avoiding `Any` is not a parametricity guarantee.

## How generics are implemented

The type checker's job is the same everywhere; the run-time strategy differs a lot.

### Erasure: Java and TypeScript; Python metadata

The compiler checks the types, then **erases** them. At run time, `List<String>` and `List<Integer>` are both just `List`, and the compiler inserts casts where values come out.

Consequences in Java:

- No `new T()` or `new T[10]`: there's no `T` at run time to construct.
- You can't test at run time whether a list is a `List<String>`; only `List<?>`.
- Overloads `f(List<String>)` and `f(List<Integer>)` clash: "same erasure".
- No primitives: `List<int>` is illegal, so ints are **boxed** into `Integer` objects, using object references; caching or existing objects can avoid a fresh allocation for each element.

Java chose erasure in 2004 for **migration compatibility**: generic code had to run on existing JVMs and interoperate with old non-generic libraries.

TypeScript erases *all* types when compiling to JavaScript, generics included. Python keeps annotations as metadata (`list[int]` is a real object you can inspect), but the interpreter never enforces them.

### Monomorphisation: Rust, C++

The compiler specializes generic code for concrete types used. Optimizers and linkers can inline, merge or eliminate instantiations, so the number of machine-code functions need not equal the number of types. `largest::<i32>` and `largest::<f64>` are distinct conceptual instantiations.

- **Pro**: zero run-time overhead, full inlining, values stored unboxed.
- **Con**: code bloat and longer compile times. More instantiations can increase compilation work; their count is not a guaranteed count of emitted functions.

Rust offers an alternative when you want one copy: `&dyn Trait` uses a **vtable** (dynamic dispatch) instead.

### Dictionary passing: Haskell

GHC compiles `Ord a => [a] -> a` to a function that takes an extra hidden argument: a **dictionary** (record) of the `Ord` methods for that type. One copy of the code, with an indirect call per comparison. The optimiser often **specialises** hot call sites to remove the overhead.

### Reification: C#/.NET

.NET keeps generic type information at run time. `typeof(T)` works, `new T()` works with a `where T : new()` constraint, and `List<int>` stores raw ints with no boxing. The usual .NET JIT strategy shares generic code across reference-type instantiations and specializes value types. Details depend on the runtime and compilation mode.

| Strategy | Languages | Run-time types? | Unboxed values? |
|---|---|---|---|
| Erasure | Java, TS | Generic arguments not reified per object; Java signature metadata may remain | Java collections use references |
| Optional hints | Python | Annotation metadata retained | Interpreter-dependent |
| Monomorphise | Rust, C++ | n/a, compiled away | Yes |
| Dictionaries | Haskell | No | Usually boxed |
| Reified | C#, .NET | Yes | Yes |

## Beyond the basics

- **Generic types**, not just functions: `struct Pair<A, B>`, `Map<K, V>`, `Result<T, E>`.
- **Higher-kinded types** abstract over type constructors themselves. Haskell's `Functor f` works for any `f` such as `Maybe` or `[]`: `fmap :: (a -> b) -> f a -> f b`. Java, TypeScript and Rust can't write this directly.
- **C++ templates** check non-dependent constructs at definition and dependent constructs during instantiation. C++20 concepts express constraints checked when a specialization is considered.

## Pitfalls

- **Needless type parameters.** The TypeScript handbook's rule: if a type parameter appears only once, you probably don't need it. `function log<T>(x: T): void` is no better than `log(x: unknown)`.
- **Raw types in Java.** Using `List` without a parameter turns off checking and produces "unchecked" warnings. Don't ignore them.
- **Boxing costs.** A Java `List<Integer>` of a million elements holds a million references; these may share cached or pre-existing objects. Use `int[]` or a primitive collection library for hot paths.
- **Monomorphisation bloat.** In Rust, very generic code in a large codebase can noticeably inflate binary size and compile times.

## Key takeaways
- Generics let one definition work for many types while the checker still tracks the specific type at each use, replacing `Object` and casts.
- Parametric polymorphism runs the same code for every type; bounds (`extends`, trait bounds, `Ord a =>`, Protocols) unlock operations on `T`.
- Parametricity means a polymorphic type constrains behaviour: `a -> a` can only be identity.
- Java and TypeScript erase generic type arguments; Python retains annotation metadata without enforcing it; Rust and C++ monomorphise; Haskell passes dictionaries; .NET reifies.
- Erasure explains Java's limits: no `new T()`, no `List<int>`, overload clashes, boxing.

## Further reading
- [Parametric polymorphism — Wikipedia](https://en.wikipedia.org/wiki/Parametric_polymorphism)
- [Generics — TypeScript handbook](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [Generic data types — The Rust Programming Language](https://doc.rust-lang.org/book/ch10-01-syntax.html)
- [Type erasure — The Java Tutorials](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)
- [PEP 695: Type parameter syntax](https://peps.python.org/pep-0695/)
- [Philip Wadler, Theorems for free! (PDF)](https://people.mpi-sws.org/~dreyer/tor/papers/wadler.pdf)
- [Generic classes and methods — C# docs, Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/generics)
- [Primary verification source 3](https://homepages.inf.ed.ac.uk/wadler/topics/parametricity.html)
- [Primary verification source 4](https://doc.rust-lang.org/std/any/fn.type_name.html)
- [Primary verification source 5](https://eel.is/c++draft/temp.res)
- [Primary verification source 7](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/generics/generics-in-the-run-time)
